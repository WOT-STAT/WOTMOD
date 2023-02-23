# coding=utf-8
import BigWorld

import datetime


class Event:
  class NAMES:
    ON_BATTLE_START = 'OnBattleStart'
    ON_SHOT = 'OnShot'
    ON_BATTLE_RESULT = 'OnBattleResult'

  def __init__(self, event_name):
    self.date = get_current_date()
    self.eventName = event_name

  def get_dict(self):
    return self.__dict__


class OnBattleStart(Event):

  def __init__(self, arenaTag, arenaId, team, playerName, playerBdid, playerClan, tankTag, tankType, tankLevel,
               gunTag, startDis, spawnPoint, battleMode, battleGameplay, gameVersion, serverName, region, modVersion,
               battlePeriod, battleTime, loadTime, preBattleWaitTime, inQueueWaitTime, gameplayMask):
    Event.__init__(self, Event.NAMES.ON_BATTLE_START)

    self.arenaTag = arenaTag
    self.arenaID = arenaId
    self.team = team
    self.playerName = playerName
    self.playerBDID = playerBdid
    self.playerClan = playerClan
    self.tankTag = tankTag
    self.tankType = tankType
    self.tankLevel = tankLevel
    self.gunTag = gunTag
    self.startDis = startDis
    self.spawnPoint = spawnPoint
    self.battleMode = battleMode
    self.battleGameplay = battleGameplay
    self.gameVersion = gameVersion
    self.serverName = serverName
    self.region = region
    self.modVersion = modVersion
    self.battlePeriod = battlePeriod
    self.battleTime = battleTime
    self.loadTime = loadTime
    self.preBattleWaitTime = preBattleWaitTime
    self.inQueueWaitTime = inQueueWaitTime
    self.gameplayMask = gameplayMask


class OnShot(Event):
  class HIT_REASON:
    TANK = 'tank'
    TERRAIN = 'terrain'

  def __init__(self):
    Event.__init__(self, Event.NAMES.ON_SHOT)

    self.battleTime = None
    self.serverMarkerPoint = None
    self.clientMarkerPoint = None
    self.serverShotDispersion = None
    self.clientShotDispersion = None

    self.shotId = None
    self.gunPoint = None
    self.battleDispersion = None
    self.gunDispersion = None
    self.shellTag = None
    self.shellName = None
    self.shellDamage = None
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

  def set_shoot(self, gun_position, battle_dispersion, shot_dispersion, shell_name, shell_tag, damage, caliber,
                piercingPower, speed, maxDistance, shell_descr, ping, fps, auto_aim, server_aim, vehicle_descr,
                chassis_descr, turret_descr, gun_descr, turret_yaw, turret_pitch, vehicle_speed, turret_speed):
    self.gunPoint = gun_position
    self.battleDispersion = battle_dispersion
    self.gunDispersion = shot_dispersion
    self.shellTag = shell_tag
    self.shellName = shell_name
    self.shellDamage = damage
    self.shellCaliber = caliber
    self.shellPiercingPower = piercingPower
    self.shellSpeed = speed
    self.shellMaxDistance = maxDistance
    self.shellDescr = shell_descr

    self.vehicleSpeed = vehicle_speed
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

  def set_date(self, date=None):
    if date:
      self.date = date
    else:
      self.date = get_current_date()

  def set_battle_time(self, time):
    self.battleTime = time


# TODO: Декодировать больше результатов
class OnBattleResult(Event):
  def __init__(self, raw=None, result=None, credits=None, xp=None, duration=None, botsCount=None):
    Event.__init__(self, Event.NAMES.ON_BATTLE_RESULT)

    self.raw = raw
    self.result = result
    self.credits = credits
    self.xp = xp
    self.duration = duration
    self.botsCount = botsCount


def get_current_date():
  return datetime.datetime.now().isoformat()  # TODO: Лучше брать серверное время танков, если такое есть
