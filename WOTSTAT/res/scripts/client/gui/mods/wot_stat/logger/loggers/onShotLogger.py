import BigWorld
from Math import Matrix
from Vehicle import Vehicle
from VehicleEffects import DamageFromShotDecoder
from constants import SERVER_TICK_LENGTH, ATTACK_REASON, ATTACK_REASON_INDICES

from ..eventLogger import eventLogger, battle_time
from ..events import OnShot
from ..utils import vector, own_gun_position
from ..wotHookEvents import wotHookEvents
from ...utils import print_debug
from ...logical.shotEventCollector import shotEventCollector
from account_helpers.settings_core.settings_constants import GAME


def own_effect_index(player):
  return map(lambda t: t.shell.effectsIndex, player.vehicleTypeDescriptor.gun.shots)


def tank_name_by_id(vehicleID):
  return BigWorld.player().arena.vehicles[vehicleID]['vehicleType'].name


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


class OnShotLogger:

  def __init__(self):
    wotHookEvents.VehicleGunRotator_updateGunMarker += self.update_gun_marker_client
    wotHookEvents.VehicleGunRotator_setShotPosition += self.update_gun_marker_server
    wotHookEvents.PlayerAvatar_shoot += self.shoot
    wotHookEvents.PlayerAvatar_showTracer += self.show_tracer
    wotHookEvents.PlayerAvatar_showShotResults += self.show_shot_results
    wotHookEvents.Vehicle_showDamageFromShot += self.show_damage_from_shot
    wotHookEvents.PlayerAvatar_explodeProjectile += self.explode_projectile
    wotHookEvents.ProjectileMover_killProjectile += self.kill_projectile
    wotHookEvents.Vehicle_onHealthChanged += self.on_health_changed

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
          onShot.set_hit_extra(vehicle_descr, chassis_descr, turret_descr, gun_descr, yaw, pitch, str(segment))

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
    self.marker_server_pos = obj._VehicleGunRotator__getGunMarkerPosition(
      shotPos, shotVec, (dispersionAngle, dispersionAngle))[0]
    self.marker_server_disp = dispersionAngle

  def update_gun_marker_client(self, obj, *a, **k):
    shotPos, shotVec = obj.getCurShotPosition()
    self.marker_client_pos = obj._VehicleGunRotator__getGunMarkerPosition(
      shotPos, shotVec, obj._VehicleGunRotator__dispersionAngles)[0]

    self.marker_client_disp = obj._VehicleGunRotator__dispersionAngles[0]

  def shoot(self, obj, isRepeat=False, *a, **k):
    can_shoot, error = obj.guiSessionProvider.shared.ammo.canShoot(isRepeat)
    if not can_shoot:
      return

    player = BigWorld.player()
    self.temp_shot.set_battle_time(battle_time())
    self.temp_shot.set_date()
    self.temp_shot.set_server_marker(vector(self.marker_server_pos), self.marker_server_disp)
    self.temp_shot.set_client_marker(vector(self.marker_client_pos), self.marker_client_disp)
    shot = player.vehicleTypeDescriptor.shot

    vehicle_descr, chassis_descr, turret_descr, gun_descr, yaw, pitch = get_full_descr(player.vehicle)
    self.temp_shot.set_shoot(gun_position=vector(own_gun_position(player)),
                             battle_dispersion=player.vehicleTypeDescriptor.gun.shotDispersionAngle,
                             shot_dispersion=(
                                 player.vehicleTypeDescriptor.gun.shotDispersionAngle *
                                 player._PlayerAvatar__aimingInfo[2]),
                             shell_name=player.vehicleTypeDescriptor.shot.shell.name,
                             shell_tag=player.vehicleTypeDescriptor.shot.shell.kind,
                             damage=str(shot.shell.damage),
                             caliber=shot.shell.caliber,
                             piercingPower=str(shot.piercingPower),
                             speed=shot.speed / 0.8,
                             maxDistance=shot.maxDistance,
                             shell_descr=shot.shell.compactDescr,
                             ping=BigWorld.LatencyInfo().value[3] - 0.5 * SERVER_TICK_LENGTH,
                             fps=BigWorld.getFPS()[1],
                             auto_aim=(player.autoAimVehicle is not None),
                             server_aim=bool(player.gunRotator.settingsCore.getSetting('useServerAim')),
                             vehicle_speed=player.getOwnVehicleSpeeds()[0] * 3.6,
                             turret_speed=player.gunRotator.turretRotationSpeed,
                             vehicle_descr=vehicle_descr,
                             chassis_descr=chassis_descr,
                             turret_descr=turret_descr,
                             gun_descr=gun_descr,
                             turret_pitch=pitch,
                             turret_yaw=yaw
                             )
    self.shot_click_time = BigWorld.serverTime()
    print_debug('shoot')

  def show_tracer(self, obj, attackerID, shotID, isRicochet, effectsIndex, refStartPoint, refVelocity, gravity, *a,
                  **k):
    player = BigWorld.player()
    if isRicochet or attackerID != player.playerVehicleID or effectsIndex not in own_effect_index(player):
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

      shotEventCollector.shot_result(vehicleID, flags)

  def on_health_changed(self, obj, newHealth, oldHealth, attackerID, attackReasonID):
    if attackerID == BigWorld.player().playerVehicleID and BigWorld.player().arena.vehicles[obj.id][
      'team'] != BigWorld.player().team:
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
