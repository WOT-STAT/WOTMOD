# coding=utf-8
import BigWorld

import datetime


class Event:
    class NAMES:
        ON_BATTLE_START = 'OnBattleStart'
        ON_SHOT = 'OnShot'
        ON_BATTLE_RESULT = 'OnBattleResult'

    def __init__(self, event_name):
        self.Date = get_current_date()
        self.EventName = event_name

    def get_dict(self):
        return self.__dict__


class OnBattleStart(Event):

    def __init__(self, ArenaTag, ArenaID, Team, PlayerName, PlayerBDID, PlayerClan, TankTag, TankType, TankLevel,
                 GunTag, StartDis, SpawnPoint, BattleMode, BattleGameplay, GameVersion, ServerName, Region, ModVersion,
                 BattlePeriod, BattleTime, LoadTime, PreBattleWaitTime, InQueueWaitTime, GameplayMask):
        Event.__init__(self, Event.NAMES.ON_BATTLE_START)

        self.ArenaTag = ArenaTag
        self.ArenaID = ArenaID
        self.Team = Team
        self.PlayerName = PlayerName
        self.PlayerBDID = PlayerBDID
        self.PlayerClan = PlayerClan
        self.TankTag = TankTag
        self.TankType = TankType
        self.TankLevel = TankLevel
        self.GunTag = GunTag
        self.StartDis = StartDis
        self.SpawnPoint = SpawnPoint
        self.BattleMode = BattleMode
        self.BattleGameplay = BattleGameplay
        self.GameVersion = GameVersion
        self.ServerName = ServerName
        self.Region = Region
        self.ModVersion = ModVersion
        self.BattlePeriod = BattlePeriod
        self.BattleTime = BattleTime
        self.LoadTime = LoadTime
        self.PreBattleWaitTime = PreBattleWaitTime
        self.InQueueWaitTime = InQueueWaitTime
        self.GameplayMask = GameplayMask

class OnShot(Event):
    class HIT_REASON:
        TANK = 'tank'
        TERRAIN = 'terrain'

    def __init__(self):
        Event.__init__(self, Event.NAMES.ON_SHOT)

        self.BattleTime = None
        self.ServerMarkerPoint = None
        self.ClientMarkerPoint = None
        self.ServerShotDispersion = None
        self.ClientShotDispersion = None

        self.ShotID = None
        self.GunPoint = None
        self.BattleDispersion = None
        self.GunDispersion = None
        self.ShellTag = None
        self.ShellName = None
        self.ShellDamage = None
        self.ShellCaliber = None
        self.ShellPiercingPower = None
        self.ShellSpeed = None
        self.ShellMaxDistance = None
        self.Ping = None
        self.FPS = None
        self.ServerAim = None
        self.AutoAim = None

        self.TracerStart = None
        self.TracerEnd = None
        self.TracerVel = None
        self.Gravity = None

        self.HitVehicleDescr = None
        self.HitChassisDescr = None
        self.HitTurretDescr = None
        self.HitGunDescr = None
        self.HitTurretYaw = None
        self.HitTurretPitch = None
        self.HitSegment = None

        self.VehicleDescr = None
        self.ChassisDescr = None
        self.TurretDescr = None
        self.GunDescr = None
        self.TurretYaw = None
        self.TurretPitch = None

        self.ShellDescr = None
        self.VehicleSpeed = None
        self.TurretSpeed = None

        self.HitPoint = None
        self.HitReason = None
        self.Results = []

    def set_client_marker(self, position, dispersion):
        self.ClientMarkerPoint = position
        self.ClientShotDispersion = dispersion

    def set_server_marker(self, position, dispersion):
        self.ServerMarkerPoint = position
        self.ServerShotDispersion = dispersion

    def set_shoot(self, gun_position, battle_dispersion, shot_dispersion, shell_name, shell_tag, damage, caliber,
                  piercingPower, speed, maxDistance, shell_descr, ping, fps, auto_aim, server_aim, vehicle_descr,
                  chassis_descr, turret_descr, gun_descr, turret_yaw, turret_pitch, vehicle_speed, turret_speed):
        self.GunPoint = gun_position
        self.BattleDispersion = battle_dispersion
        self.GunDispersion = shot_dispersion
        self.ShellTag = shell_tag
        self.ShellName = shell_name
        self.ShellDamage = damage
        self.ShellCaliber = caliber
        self.ShellPiercingPower = piercingPower
        self.ShellSpeed = speed
        self.ShellMaxDistance = maxDistance
        self.ShellDescr = shell_descr

        self.VehicleSpeed = vehicle_speed
        self.TurretSpeed = turret_speed

        self.Ping = ping
        self.FPS = fps
        self.AutoAim = auto_aim
        self.ServerAim = server_aim

        self.VehicleDescr = vehicle_descr
        self.ChassisDescr = chassis_descr
        self.TurretDescr = turret_descr
        self.GunDescr = gun_descr
        self.TurretYaw = turret_yaw
        self.TurretPitch = turret_pitch

    def set_tracer(self, shot_id, start, velocity, gravity):
        self.ShotID = shot_id
        self.TracerStart = start
        self.TracerVel = velocity
        self.Gravity = gravity

    def set_hit(self, position, reason):
        self.HitPoint = position
        self.HitReason = reason

    def set_tracer_end(self, position):
        self.TracerEnd = position

    def set_hit_extra(self, vehicle_descr, chassis_descr, turret_descr, gun_descr, turret_yaw, turret_pitch, segment):
        self.HitVehicleDescr = vehicle_descr
        self.HitChassisDescr = chassis_descr
        self.HitTurretDescr = turret_descr
        self.HitGunDescr = gun_descr
        self.HitTurretYaw = turret_yaw
        self.HitTurretPitch = turret_pitch
        self.HitSegment = segment

    def add_result(self, tankTag, flags, shotDamage, fireDamage, ammoBayDestroyed, health, fireHealth):
        self.Results.append({'order': len(self.Results),
                             'tankTag': tankTag,
                             'flags': flags,
                             'shotDamage': shotDamage,
                             'fireDamage': fireDamage,
                             'ammoBayDestroyed': ammoBayDestroyed,
                             'shotHealth': health,
                             'fireHealth': fireHealth})

    def set_date(self, date=None):
        if date:
            self.Date = date
        else:
            self.Date = get_current_date()

    def set_battle_time(self, time):
        self.BattleTime = time


# TODO: Декодировать больше результатов
class OnBattleResult(Event):
    def __init__(self, RAW=None, Result=None, Credits=None, XP=None, Duration=None, BotsCount=None):
        Event.__init__(self, Event.NAMES.ON_BATTLE_RESULT)

        self.RAW = RAW
        self.Result = Result
        self.Credits = Credits
        self.XP = XP
        self.Duration = Duration
        self.BotsCount = BotsCount


def get_current_date():
    return datetime.datetime.now().isoformat()  # TODO: Лучше брать серверное время танков, если такое есть
