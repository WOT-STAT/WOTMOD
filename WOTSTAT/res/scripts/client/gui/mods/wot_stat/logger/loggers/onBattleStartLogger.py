import BattleReplay
import BigWorld
from account_shared import readClientServerVersion
from PlayerEvents import g_playerEvents
from account_helpers import gameplay_ctx
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

    self.on_enter_queue_time = 0  # Вход в очередь
    self.on_enter_world_time = 0  # Вход в бой
    self.on_end_load_time = 0  # Завершение загрузки
    self.shot_disp_multiplier_factor = 0

    wotHookEvents.PlayerAvatar_onEnterWorld += self.on_enter_world
    wotHookEvents.PlayerAvatar_updateTargetingInfo += self.update_targeting_info
    wotHookEvents.PlayerAvatar_onArenaPeriodChange += self.on_arena_period_change
    g_playerEvents.onEnqueued += self.onEnqueued

  def onEnqueued(self, queueType):
    self.on_enter_queue_time = BigWorld.serverTime()

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
    onBattleStart = OnBattleStart(arenaTag=player.arena.arenaType.geometry,
                                  arenaId=player.arenaUniqueID,
                                  team=player.team,
                                  playerName=player.name,
                                  playerBdid=player.arena.vehicles[player.playerVehicleID]['accountDBID'],
                                  playerClan=player.arena.vehicles[player.playerVehicleID]['clanAbbrev'],
                                  tankTag=BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name,
                                  tankType=short_tank_type(get_tank_type(player.vehicleTypeDescriptor.type.tags)),
                                  tankLevel=player.vehicleTypeDescriptor.level,
                                  gunTag=player.vehicleTypeDescriptor.gun.name,
                                  startDis=player.vehicleTypeDescriptor.gun.shotDispersionAngle * self.shot_disp_multiplier_factor,
                                  spawnPoint=vector(player.getOwnVehiclePosition()),
                                  battleMode=ARENA_TAGS[player.arena.bonusType],
                                  battleGameplay=ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
                                  gameVersion=readClientServerVersion()[1],
                                  serverName=player.connectionMgr.serverUserName,
                                  region=AUTH_REALM,
                                  modVersion=config.get('version'),
                                  battlePeriod=ARENA_PERIOD_NAMES[player.arena.period],
                                  battleTime=battle_time(),
                                  loadTime=self.on_end_load_time - self.on_enter_world_time,
                                  preBattleWaitTime=BigWorld.serverTime() - self.on_end_load_time,
                                  inQueueWaitTime=self.on_enter_world_time - self.on_enter_queue_time,
                                  gameplayMask=gameplay_ctx.getMask()
                                  )
    eventLogger.emit_event(onBattleStart)


onBattleStartLogger = OnBattleStartLogger()
