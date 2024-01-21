# coding=utf-8
import BigWorld

import datetime


class Event:
  class NAMES:
    ON_BATTLE_START = 'OnBattleStart'
    ON_SHOT = 'OnShot'
    ON_BATTLE_RESULT = 'OnBattleResult'

  def __init__(self, event_name):
    self.localtime = get_current_date()
    self.eventName = event_name

  def get_dict(self):
    return self.__dict__


class BattleEvent(Event):
  def __init__(self, event_name, battleTime):
    Event.__init__(self, event_name)
    self.battleTime = battleTime


class DynamicBattleEvent(BattleEvent):
  def __init__(self, event_name, battleTime):
    BattleEvent.__init__(self, event_name, battleTime)
    self.arenaTag = None
    self.playerName = None
    self.playerClan = None
    self.accountDBID = None
    self.battleMode = None
    self.battleGameplay = None
    self.serverName = None
    self.region = None
    self.gameVersion = None
    self.modVersion = None
    self.team = None
    self.tankTag = None
    self.tankType = None
    self.tankLevel = None
    self.gunTag = None

  def setupDynamicBattleInfo(self, arenaTag, playerName, playerClan, accountDBID, battleMode, battleGameplay,
                             serverName, region, gameVersion, modVersion, team, tankTag, tankType, tankLevel, gunTag):
    self.arenaTag = arenaTag
    self.playerName = playerName
    self.playerClan = playerClan
    self.accountDBID = accountDBID
    self.battleMode = battleMode
    self.battleGameplay = battleGameplay
    self.serverName = serverName
    self.region = region
    self.gameVersion = gameVersion
    self.modVersion = modVersion
    self.team = team
    self.tankTag = tankTag
    self.tankType = tankType
    self.tankLevel = tankLevel
    self.gunTag = gunTag


class OnBattleStart(DynamicBattleEvent):

  def __init__(self, arenaId, spawnPoint, battleTime,
               battlePeriod, loadTime, preBattleWaitTime, inQueueWaitTime, gameplayMask):
    DynamicBattleEvent.__init__(self, Event.NAMES.ON_BATTLE_START, battleTime)

    self.arenaID = arenaId
    self.spawnPoint = spawnPoint
    self.battlePeriod = battlePeriod
    self.loadTime = loadTime
    self.preBattleWaitTime = preBattleWaitTime
    self.inQueueWaitTime = inQueueWaitTime
    self.gameplayMask = gameplayMask


class OnShot(DynamicBattleEvent):
  class HIT_REASON:
    TANK = 'tank'
    TERRAIN = 'terrain'

  def __init__(self):
    BattleEvent.__init__(self, Event.NAMES.ON_SHOT, 0)

    self.battleTime = None
    self.serverMarkerPoint = None
    self.clientMarkerPoint = None
    self.serverShotDispersion = None
    self.clientShotDispersion = None
    self.health = None

    self.shotId = None
    self.gunPoint = None
    self.battleDispersion = None
    self.gunDispersion = None
    self.shellTag = None
    self.shellName = None
    self.shellDamage = None
    self.damageRandomization = None
    self.shellCaliber = None
    self.shellPiercingPower = None
    self.shellSpeed = None
    self.shellMaxDistance = None
    self.ping = None
    self.fps = None
    self.serverAim = None
    self.autoAim = None

    self.tracerStart = None
    self.tracerEnd = None
    self.tracerVel = None
    self.gravity = None

    self.hitVehicleDescr = None
    self.hitChassisDescr = None
    self.hitTurretDescr = None
    self.hitGunDescr = None
    self.hitTurretYaw = None
    self.hitTurretPitch = None
    self.hitSegment = None

    self.vehicleDescr = None
    self.chassisDescr = None
    self.turretDescr = None
    self.gunDescr = None
    self.turretYaw = None
    self.turretPitch = None

    self.shellDescr = None
    self.vehicleSpeed = None
    self.vehicleRotationSpeed = None
    self.turretSpeed = None

    self.hitPoint = None
    self.hitReason = None
    self.results = []

  def set_client_marker(self, position, dispersion):
    self.clientMarkerPoint = position
    self.clientShotDispersion = dispersion

  def set_server_marker(self, position, dispersion):
    self.serverMarkerPoint = position
    self.serverShotDispersion = dispersion

  def set_shoot(self, gun_position, health, battle_dispersion, shot_dispersion, shell_name, shell_tag, damage,
                damageRandomization, caliber, piercingPower, speed, maxDistance, shell_descr, ping, fps, auto_aim,
                server_aim, vehicle_descr, chassis_descr, turret_descr, gun_descr, turret_yaw, turret_pitch,
                vehicle_speed, vehicleRotationSpeed, turret_speed):
    self.gunPoint = gun_position
    self.health = health
    self.battleDispersion = battle_dispersion
    self.gunDispersion = shot_dispersion
    self.shellTag = shell_tag
    self.shellName = shell_name
    self.shellDamage = damage
    self.damageRandomization = damageRandomization
    self.shellCaliber = caliber
    self.shellPiercingPower = piercingPower
    self.shellSpeed = speed
    self.shellMaxDistance = maxDistance
    self.shellDescr = shell_descr

    self.vehicleSpeed = vehicle_speed
    self.vehicleRotationSpeed = vehicleRotationSpeed
    self.turretSpeed = turret_speed

    self.ping = ping
    self.fps = fps
    self.autoAim = auto_aim
    self.serverAim = server_aim

    self.vehicleDescr = vehicle_descr
    self.chassisDescr = chassis_descr
    self.turretDescr = turret_descr
    self.gunDescr = gun_descr
    self.turretYaw = turret_yaw
    self.turretPitch = turret_pitch

  def set_tracer(self, shot_id, start, velocity, gravity):
    self.shotId = shot_id
    self.tracerStart = start
    self.tracerVel = velocity
    self.gravity = gravity

  def set_hit(self, position, reason):
    self.hitPoint = position
    self.hitReason = reason

  def set_tracer_end(self, position):
    self.tracerEnd = position

  def set_hit_extra(self, vehicle_descr, chassis_descr, turret_descr, gun_descr, turret_yaw, turret_pitch, segment):
    self.hitVehicleDescr = vehicle_descr
    self.hitChassisDescr = chassis_descr
    self.hitTurretDescr = turret_descr
    self.hitGunDescr = gun_descr
    self.hitTurretYaw = turret_yaw
    self.hitTurretPitch = turret_pitch
    self.hitSegment = segment

  def add_result(self, tankTag, flags, shotDamage, fireDamage, ammoBayDestroyed, health, fireHealth):
    self.results.append({'order': len(self.results),
                         'tankTag': tankTag,
                         'flags': flags,
                         'shotDamage': shotDamage,
                         'fireDamage': fireDamage,
                         'ammoBayDestroyed': ammoBayDestroyed,
                         'shotHealth': health,
                         'fireHealth': fireHealth})

  def set_battle_time(self, time):
    self.battleTime = time


# TODO: Декодировать больше результатов
class OnBattleResult(DynamicBattleEvent):
  raw = None
  result = None

  def __init__(self):
    Event.__init__(self, Event.NAMES.ON_BATTLE_RESULT)

  def set_result(self, raw, result):
    self.raw = raw
    self.result = result


def get_current_date():
  return datetime.datetime.now().isoformat()  # TODO: Лучше брать серверное время танков, если такое есть
