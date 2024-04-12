import math

import BigWorld
from Avatar import getVehicleShootingPositions
from Math import Matrix
from Vehicle import Vehicle
from VehicleEffects import DamageFromShotDecoder
from constants import SERVER_TICK_LENGTH, ATTACK_REASON, ATTACK_REASON_INDICES, ARENA_PERIOD
from ..eventLogger import eventLogger, battle_time
from ..events import OnShot
from ..sessionStorage import sessionStorage
from ..utils import vector, setup_dynamic_battle_info, setup_session_meta
from ..wotHookEvents import wotHookEvents
from ...logical.shotEventCollector import shotEventCollector
from ...utils import print_debug, print_warn


def own_effect_index(player):
  return map(lambda t: t.shell.effectsIndex, player.vehicleTypeDescriptor.gun.shots)


def tank_name_by_id(vehicleID):
  vehicle = BigWorld.player().arena.vehicles[vehicleID]
  if not vehicle: return 'unknown'
  return vehicle['vehicleType'].name


def decode_hit_point(obj, decodedPoints):
  firstHitPoint = decodedPoints[0]
  compMatrix = Matrix(obj.appearance.compoundModel.node(firstHitPoint.componentName))
  firstHitDirLocal = firstHitPoint.matrix.applyToAxis(2)
  firstHitDir = compMatrix.applyVector(firstHitDirLocal)
  firstHitDir.normalise()
  return compMatrix.applyPoint(firstHitPoint.matrix.translation)


def get_full_descr(obj):
  # type: (Vehicle) -> Tuple[Any, Any, Any, Any, Any, Any]
  descr = obj.typeDescriptor
  yaw, pitch = obj.getServerGunAngles()
  return (descr.type.compactDescr, descr.chassis.compactDescr, descr.turret.compactDescr, descr.gun.compactDescr,
          yaw, pitch)


def on_enable_server_aim(obj, enable, *a, **k):
  if not enable:
    print_debug('Enable server aim info receiving')
    BigWorld.player().enableServerAim(True)


def get_player_vehicle():
  player = BigWorld.player()

  if hasattr(player, 'vehicle') and player.vehicle is not None:
    return player.vehicle

  if hasattr(player, 'playerVehicleID') and player.playerVehicleID is not None:
    entity = BigWorld.entity(player.playerVehicleID)
    if entity is not None and isinstance(entity, Vehicle) and entity.isPlayerVehicle:
      return entity

  return None


class OnShotLogger:

  def __init__(self):
    wotHookEvents.VehicleGunRotator_updateGunMarker += self.update_gun_marker_client
    wotHookEvents.PlayerAvatar_updateGunMarker += self.update_gun_marker_server
    wotHookEvents.PlayerAvatar_shoot += self.shoot
    wotHookEvents.PlayerAvatar_showTracer += self.show_tracer
    wotHookEvents.PlayerAvatar_showShotResults += self.show_shot_results
    wotHookEvents.Vehicle_showDamageFromShot += self.show_damage_from_shot
    wotHookEvents.PlayerAvatar_explodeProjectile += self.explode_projectile
    wotHookEvents.ProjectileMover_killProjectile += self.kill_projectile
    wotHookEvents.Vehicle_onHealthChanged += self.on_health_changed
    wotHookEvents.PlayerAvatar_onArenaPeriodChange += self.on_arena_period_change
    wotHookEvents.PlayerAvatar_enableServerAim += on_enable_server_aim
    wotHookEvents.PlayerAvatar_onEnterWorld += self.on_enter_world

    self.marker_server_pos = None
    self.marker_server_disp = None
    self.marker_client_pos = None
    self.marker_client_disp = None

    self.shot_click_time = 0
    self.temp_shot = OnShot()
    self.shots = dict()

    self.check_shot_result()

    self.active_tracers = []
    self.history_tracers = []

    self.cachedVehicle = None

  def on_enter_world(self, obj, *a, **k):
    self.cachedVehicle = None
    self.active_tracers = []
    self.history_tracers = []
    self.marker_server_disp = None
    self.marker_server_pos = None
    self.marker_client_disp = None
    self.marker_client_pos = None
    BigWorld.player().enableServerAim(True)

  def on_arena_period_change(self, obj, period, *a, **k):
    if period is ARENA_PERIOD.BATTLE:
      self.cachedVehicle = BigWorld.player().vehicle

  def check_shot_result(self):
    BigWorld.callback(1, self.check_shot_result)
    shotEventCollector.process_events()
    results = shotEventCollector.get_result()
    if results:
      for r in results:
        shotID = r['shotID']
        if shotID not in self.shots:
          continue

        onShot = self.shots.pop(shotID)  # type: OnShot

        if r['tank_hit_point']:
          onShot.set_hit(vector(r['tank_hit_point']), OnShot.HIT_REASON.TANK)
        elif r['terrain_hit_point']:
          onShot.set_hit(vector(r['terrain_hit_point']), OnShot.HIT_REASON.TERRAIN)

        if r['tracer_end_point']: onShot.set_tracer_end(vector(r['tracer_end_point']))
        if r['tank_hit_extra']:
          vehicle_descr, chassis_descr, turret_descr, gun_descr, yaw, pitch, segment = r['tank_hit_extra']
          onShot.set_hit_extra(vehicle_descr, chassis_descr, turret_descr, gun_descr, yaw, pitch,
                               str(segment))

        def acc(a, v):
          a[v['vehicleID']] = v
          return a

        damage_dict = reduce(acc, r['damages'], dict())
        fire_damage_dict = reduce(acc, r['fire_damages'], dict())
        for results in r['shot_results']:
          damage = damage_dict.get(results['vehicleID'], None)
          fire_damage = fire_damage_dict.get(results['vehicleID'], None)
          onShot.add_result(tankTag=tank_name_by_id(results['vehicleID']),
                            flags=results['flags'],
                            shotDamage=damage['damage'] if damage else 0,
                            fireDamage=fire_damage['damage'] if fire_damage else 0,
                            ammoBayDestroyed=(damage['ammo_bay_destr'] if damage else False) or (
                              fire_damage['ammo_bay_destr'] if fire_damage else False),
                            health=damage['newHealth'] if damage else None,
                            fireHealth=fire_damage['newHealth'] if fire_damage else None)

        if not onShot.accountDBID or not onShot.tracerEnd:
          print_debug('SHOT IS NOT INIT. ERROR')
          continue

        sessionStorage.on_shot(has_damage=len(filter(lambda t: t['damage'] > 0, r['damages'])) != 0,
                               has_direct_hit=len(r['damages']) > 0)
        eventLogger.emit_event(onShot)

        log = ""
        log += "________________RESULT_________________\n"
        log += ("status: %s\n" % r['status'])
        if r['tank_hit_point']: log += ("tank_hit_point: %s\n" % r['tank_hit_point'])
        if r['terrain_hit_point']: log += ("terrain_hit_point: %s\n" % r['terrain_hit_point'])
        if r['tracer_end_point']: log += ("tracer_end_point: %s\n" % r['tracer_end_point'])
        log += ("total_damage: %s\n" % r['total_damage'])
        log += ("damages: %s\n" % len(r['damages']))
        for d in r['damages']:
          log += ('\t%s\n' % str(d))
        log += ("fire: %s\n" % len(r['fire_damages']))
        for d in r['fire_damages']:
          log += ('\t%s\n' % str(d))
        log += "_______________________________________"

        print_debug(log)

  def update_gun_marker_server(self, obj, vehicleID, shotPos, shotVec, dispersionAngle, *a, **k):
    if not obj.gunRotator: return
    self.marker_server_pos = obj.gunRotator._VehicleGunRotator__getGunMarkerPosition(
      shotPos, shotVec, [dispersionAngle, dispersionAngle, dispersionAngle, dispersionAngle])[0]

    self.marker_server_disp = dispersionAngle

  def update_gun_marker_client(self, obj, *a, **k):
    shotPos, shotVec = obj.getCurShotPosition()
    self.marker_client_pos = obj._VehicleGunRotator__getGunMarkerPosition(
      shotPos, shotVec, obj._VehicleGunRotator__dispersionAngles)[0]

    self.marker_client_disp = obj._VehicleGunRotator__dispersionAngles[0]

  def shoot(self, obj, isRepeat=False, *a, **k):
    can_shoot, error = obj.guiSessionProvider.shared.ammo.canShoot(isRepeat)

    if not can_shoot or \
        obj._PlayerAvatar__gunReloadCommandWaitEndTime > BigWorld.time() or \
        obj._PlayerAvatar__shotWaitingTimerID is not None or \
        obj._PlayerAvatar__isWaitingForShot or \
        obj._PlayerAvatar__chargeWaitingTimerID is not None or \
        obj._PlayerAvatar__isOwnBarrelUnderWater() or \
        obj.isGunLocked or \
        obj._PlayerAvatar__isOwnVehicleSwitchingSiegeMode():
      return

    if self.marker_server_pos is None or \
        self.marker_server_disp is None or \
        self.marker_client_pos is None or \
        self.marker_client_disp is None:
      print_warn('Marker is None %s' % str(
        (self.marker_server_pos, self.marker_server_disp, self.marker_client_pos, self.marker_client_disp)))
      return

    player = BigWorld.player()
    self.temp_shot.set_battle_time(battle_time())
    self.temp_shot.set_server_marker(vector(self.marker_server_pos), self.marker_server_disp)
    self.temp_shot.set_client_marker(vector(self.marker_client_pos), self.marker_client_disp)
    setup_dynamic_battle_info(self.temp_shot)
    setup_session_meta(self.temp_shot)
    shot = player.vehicleTypeDescriptor.shot

    player_vehicle = get_player_vehicle()
    if player_vehicle is not None:
      self.cachedVehicle = player_vehicle
    elif self.cachedVehicle is not None:
      player_vehicle = self.cachedVehicle
    else:
      print_warn("Can not get player vehicle")
      return

    vehicle_descr, chassis_descr, turret_descr, gun_descr, yaw, pitch = get_full_descr(player_vehicle)
    shot_dispersion = player.vehicleTypeDescriptor.gun.shotDispersionAngle * player._PlayerAvatar__dispersionInfo[0]
    gun_position = getVehicleShootingPositions(player_vehicle)[0]

    self.temp_shot.set_shoot(gun_position=vector(gun_position),
                             health=player_vehicle.health,
                             battle_dispersion=player.vehicleTypeDescriptor.gun.shotDispersionAngle,
                             shot_dispersion=shot_dispersion,
                             shell_name=player.vehicleTypeDescriptor.shot.shell.name,
                             shell_tag=player.vehicleTypeDescriptor.shot.shell.kind,
                             damage=shot.shell.armorDamage[0] if hasattr(shot.shell, 'armorDamage') else
                             shot.shell.damage[0],
                             damage_randomization=shot.shell.damageRandomization,
                             caliber=shot.shell.caliber,
                             piercing_power=shot.piercingPower[0],
                             speed=shot.speed / 0.8,
                             max_distance=int(shot.maxDistance),
                             shell_descr=shot.shell.compactDescr,
                             ping=BigWorld.LatencyInfo().value[3] - 0.5 * SERVER_TICK_LENGTH,
                             fps=int(BigWorld.getFPS()[1]),
                             auto_aim=(player.autoAimVehicle is not None),
                             server_aim=bool(player.gunRotator.settingsCore.getSetting('useServerAim')),
                             vehicle_speed=player.getOwnVehicleSpeeds()[0] * 3.6,
                             vehicle_rotation_speed=player.getOwnVehicleSpeeds()[1] * 180 / math.pi,
                             turret_speed=player.gunRotator.turretRotationSpeed * 180 / math.pi,
                             vehicle_descr=vehicle_descr,
                             chassis_descr=chassis_descr,
                             turret_descr=turret_descr,
                             gun_descr=gun_descr,
                             turret_pitch=pitch,
                             turret_yaw=yaw
                             )
    self.shot_click_time = BigWorld.serverTime()

    print_debug(
      '[shoot]\nhealth: %s\nserver_dispersion: %s\nclient_dispersion: %s\nturret_speed: %s\nvehicle_speed: %s\nvehicle_rotation_speed: %s' % (
        player_vehicle.health,
        self.marker_server_disp / shot_dispersion if self.marker_server_disp else None,
        self.marker_client_disp / shot_dispersion if self.marker_client_disp else None,
        player.gunRotator.turretRotationSpeed * 180 / math.pi,
        player.getOwnVehicleSpeeds()[0] * 3.6,
        player.getOwnVehicleSpeeds()[1] * 180 / math.pi
      ))

  def show_tracer(self, obj, attackerID, shotID, isRicochet, effectsIndex, refStartPoint, refVelocity, gravity, *a, **k):
    player = BigWorld.player()
    if isRicochet or player is None or attackerID != player.playerVehicleID or effectsIndex not in own_effect_index(player):
      return

    shot = abs(shotID)
    shotEventCollector.show_tracer(shot, refStartPoint, refVelocity, gravity, self.shot_click_time)
    self.active_tracers.append(shot)
    self.history_tracers.append(shot)

    self.temp_shot.set_tracer(shot, vector(refStartPoint), vector(refVelocity), gravity)
    self.shots[shot] = self.temp_shot
    self.temp_shot = OnShot()

  def show_shot_results(self, obj, results):
    for r in results:
      mask = ((1 << 32) - 1)
      vehicleID = r & mask
      flags = r >> 32 & mask

      vehicle = BigWorld.entities.get(vehicleID)
      health = vehicle.health if vehicle else None
      shotEventCollector.shot_result(vehicleID, flags, health)

  def on_health_changed(self, obj, newHealth, oldHealth, attackerID, attackReasonID):
    vehicle = BigWorld.player().arena.vehicles[obj.id]
    if attackerID == BigWorld.player().playerVehicleID and (not vehicle or vehicle['team'] != BigWorld.player().team):
      if attackReasonID == ATTACK_REASON_INDICES[ATTACK_REASON.SHOT]:
        shotEventCollector.shot_damage(obj.id, newHealth, oldHealth)
      if attackReasonID == ATTACK_REASON_INDICES[ATTACK_REASON.FIRE]:
        shotEventCollector.fire_damage(obj.id, newHealth, oldHealth)

  def explode_projectile(self, obj, shotID, effectsIndex, effectMaterialIndex, endPoint, *a, **k):
    if effectsIndex not in own_effect_index(BigWorld.player()):
      return

    if shotID in self.history_tracers:
      self.history_tracers.remove(shotID)
      shotEventCollector.terrain_hit(shotID, endPoint)

  def show_damage_from_shot(self, obj, attackerID, points, effectsIndex, *a, **k):
    player = BigWorld.player()

    if attackerID != player.playerVehicleID or effectsIndex not in own_effect_index(player):
      return

    if not obj.isStarted:
      return

    decodedPoints = DamageFromShotDecoder.decodeHitPoints(points, obj.appearance.collisions)
    if not decodedPoints:
      return

    shotEventCollector.tank_hit(obj.id, decode_hit_point(obj, decodedPoints), get_full_descr(obj) + (points[0],))

  def kill_projectile(self, obj, shotID, position, impactVelDir, deathType, *a, **k):
    shot = abs(shotID)
    if shot in self.active_tracers:
      self.active_tracers.remove(shot)
      shotEventCollector.hide_tracer(shotID, position)


onShotLogger = OnShotLogger()
