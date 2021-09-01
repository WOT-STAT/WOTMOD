# coding=utf-8
import BigWorld

import datetime


class Event:
    def __init__(self, event_name):
        self.Date = get_current_date()
        self.EventName = event_name

    def get_dict(self):
        return self.__dict__


class OnEndLoad(Event):

    def __init__(self, ArenaTag, ArenaID, Team, PlayerName, PlayerBDID, PlayerClan, TankTag, TankType, TankLevel,
                 GunTag, StartDis, SpawnPoint, TimerToStart, BattleMode, GameVersion, ModVersion):
        Event.__init__(self, 'OnEndLoad')

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
        self.TimerToStart = TimerToStart
        self.BattleMode = BattleMode
        self.GameVersion = GameVersion
        self.ModVersion = ModVersion


# Жизненный цикл события OnShot:
# 1. На PlayerAvatar.shoot устанавливает состояние маркера и состояние текущего снаряда "на момент перед выстрелом" (set_client_marker, set_server_marker, set_shoot)
# 2. На PlayerAvatar.showTracer устаналивается состояние трассера (set_tracer)
# 3. [Опционально] На PlayerAvatar.explodeProjectile попал в рельеф (set_hit)
#    [Опционально] На Vehicle.showDamageFromShot Попал в танк (set_hit)
# 4. На ProjectileMover.killProjectile событие сформировано (set_tracer_end)
class OnShot(Event):

    def __init__(self, ServerMarkerPoint=None, ClientMarkerPoint=None, ServerShotDispersion=None,
                 ClientShotDispersion=None, ShotID=None, GunPoint=None, BattleDispersion=None, GunDispersion=None,
                 ShellTag=None, Ping=None, ServerAim=None, AutoAim=None, TracerStart=None, TracerEnd=None,
                 TracerVel=None, Gravity=None, HitPoint=None, HitReason=None):
        Event.__init__(self, 'OnShot')

        self.ServerMarkerPoint = ServerMarkerPoint
        self.ClientMarkerPoint = ClientMarkerPoint
        self.ServerShotDispersion = ServerShotDispersion
        self.ClientShotDispersion = ClientShotDispersion

        self.ShotID = ShotID
        self.GunPoint = GunPoint
        self.BattleDispersion = BattleDispersion
        self.GunDispersion = GunDispersion
        self.ShellTag = ShellTag
        self.Ping = Ping
        self.ServerAim = ServerAim
        self.AutoAim = AutoAim

        self.TracerStart = TracerStart
        self.TracerEnd = TracerEnd
        self.TracerVel = TracerVel
        self.Gravity = Gravity

        self.HitPoint = HitPoint
        self.HitReason = HitReason

    def set_client_marker(self, position, dispersion):
        self.ClientMarkerPoint = position
        self.ClientShotDispersion = dispersion

        return self

    def set_server_marker(self, position, dispersion):
        self.ServerMarkerPoint = position
        self.ServerShotDispersion = dispersion

        return self

    def set_shoot(self, gun_position, battle_dispersion, shot_dispersion, shell_name, shell_tag, ping,
                  auto_aim, server_aim):
        self.GunPoint = gun_position
        self.BattleDispersion = battle_dispersion
        self.GunDispersion = shot_dispersion
        self.ShellTag = shell_tag

        self.Ping = ping
        self.AutoAim = auto_aim
        self.ServerAim = server_aim

        return self

    def set_tracer(self, shot_id, start, velocity, gravity):
        self.ShotID = shot_id
        self.TracerStart = start
        self.TracerVel = velocity
        self.Gravity = gravity

        return self

    def set_hit(self, position, reason):
        self.HitPoint = position
        self.HitReason = reason

        return self

    def set_tracer_end(self, position):
        self.TracerEnd = position

        return self

    def set_date(self, date=None):
        if date:
            self.Date = date
        else:
            self.Date = get_current_date()

#TODO: Декодировать больше результатов
class OnBattleResult(Event):
    def __init__(self, RAW=None, Result=None, Credits=None, XP=None, Duration=None, BotsCount=None):
        Event.__init__(self, 'OnBattleResult')

        self.RAW = RAW
        self.Result = Result
        self.Credits = Credits
        self.XP = XP
        self.Duration = Duration
        self.BotsCount = BotsCount


def get_current_date():
    return datetime.datetime.now().isoformat()  # TODO: Лучше брать серверное время танков, если такое есть
