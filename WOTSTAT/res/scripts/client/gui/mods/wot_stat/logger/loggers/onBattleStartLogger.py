# coding=utf-8
import BattleReplay
import BigWorld
from account_shared import readClientServerVersion
from constants import ARENA_PERIOD, ARENA_GAMEPLAY_NAMES, AUTH_REALM, ARENA_PERIOD_NAMES

from ..eventLogger import eventLogger, battle_time
from ..events import OnBattleStart
from ..utils import short_tank_type, get_tank_type, vector, ARENA_TAGS
from ..wotHookEvents import wotHookEvents
from ...load_mod import config
from ...utils import print_log, print_debug


class OnBattleStartLogger:
    def __init__(self):
        self.battle_loaded = False

        self.on_enter_world_time = 0  # Вход в бой
        self.on_end_load_time = 0  # Завершение загрузки
        self.shot_disp_multiplier_factor = 0

        wotHookEvents.PlayerAvatar_onEnterWorld += self.on_enter_world
        wotHookEvents.PlayerAvatar_updateTargetingInfo += self.update_targeting_info
        wotHookEvents.PlayerAvatar_onArenaPeriodChange += self.on_arena_period_change

    def on_enter_world(self, obj, *a, **k):
        print_debug('OnBattleStartLogger.on_enter_world')

        self.battle_loaded = False
        self.on_enter_world_time = BigWorld.serverTime()

    def update_targeting_info(self, obj, turretYaw, gunPitch, maxTurretRotationSpeed, maxGunRotationSpeed,
                              shot_disp_multiplier_factor, *a, **k):
        if BattleReplay.isPlaying():
            return
        if not hasattr(BigWorld.player(), 'arena') or not BigWorld.player().getOwnVehiclePosition():
            return
        if self.battle_loaded:
            return

        print_debug("______OnEndLoad______")
        self.battle_loaded = True
        self.on_end_load_time = BigWorld.serverTime()
        self.shot_disp_multiplier_factor = shot_disp_multiplier_factor

        if BigWorld.player().arena.period in [ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE]:
            self.init_battle_session()

    def on_arena_period_change(self, obj, period, periodEndTime, periodLength, periodAdditionalInfo, *a, **k):
        if period is ARENA_PERIOD.PREBATTLE:
            self.init_battle_session()
        if period is ARENA_PERIOD.BATTLE:
            eventLogger.start_battle_time = periodEndTime - periodLength

    def init_battle_session(self):
        if not self.battle_loaded:
            return

        print_debug("______INIT______")

        player = BigWorld.player()

        eventLogger.start_battle_time = player.arena.periodEndTime \
            if player.arena.period is ARENA_PERIOD.PREBATTLE \
            else player.arena.periodEndTime - player.arena.periodLength


        player.enableServerAim(True)
        onBattleStart = OnBattleStart(ArenaTag=player.arena.arenaType.geometry,
                                      ArenaID=player.arenaUniqueID,
                                      Team=player.team,
                                      PlayerName=player.name,
                                      PlayerBDID=player.arena.vehicles[player.playerVehicleID]['accountDBID'],
                                      PlayerClan=player.arena.vehicles[player.playerVehicleID]['clanAbbrev'],
                                      TankTag=BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name,
                                      TankType=short_tank_type(get_tank_type(player.vehicleTypeDescriptor.type.tags)),
                                      TankLevel=player.vehicleTypeDescriptor.level,
                                      GunTag=player.vehicleTypeDescriptor.gun.name,
                                      StartDis=player.vehicleTypeDescriptor.gun.shotDispersionAngle * self.shot_disp_multiplier_factor,
                                      SpawnPoint=vector(player.getOwnVehiclePosition()),
                                      BattleMode=ARENA_TAGS[player.arena.bonusType],
                                      BattleGameplay=ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
                                      GameVersion=readClientServerVersion()[1],
                                      ServerName=player.connectionMgr.serverUserName,
                                      Region=AUTH_REALM,
                                      ModVersion=config.get('version'),
                                      BattlePeriod=ARENA_PERIOD_NAMES[player.arena.period],
                                      BattleTime=battle_time(),
                                      LoadTime=self.on_end_load_time - self.on_enter_world_time,
                                      PreBattleWaitTime=BigWorld.serverTime() - self.on_end_load_time
                                      )
        eventLogger.emit_event(onBattleStart)


onBattleStartLogger = OnBattleStartLogger()
