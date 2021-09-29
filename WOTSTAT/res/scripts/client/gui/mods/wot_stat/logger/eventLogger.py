# coding=utf-8
import BigWorld
import BattleReplay
import Event
from account_shared import readClientServerVersion
from VehicleEffects import DamageFromShotDecoder
from vehicle_systems.tankStructure import TankPartNames
from Math import Matrix, Vector3
from PlayerEvents import g_playerEvents
from functools import partial
from constants import ARENA_PERIOD, ARENA_PERIOD_NAMES, ARENA_GAMEPLAY_NAMES, AUTH_REALM, SERVER_TICK_LENGTH

from events import OnBattleStart, OnShot, OnBattleResult
from battleEventSession import BattleEventSession
from wotHookEvents import wotHookEvents
from ..load_mod import config
from ..utils import print_log, print_debug
from .utils import *

class EventLogger:
    old_battle_event_sessions = {}
    battle_event_session = None  # type: BattleEventSession
    start_battle_time = 0
    on_session_created = Event.Event()

    def __init__(self):
        print_debug('INIT EVENT LOGGER')

    def emit_event(self, event, arena_id=None):
        if event.EventName == 'OnBattleStart':
            if self.battle_event_session:
                self.old_battle_event_sessions[self.battle_event_session.arenaID] = self.battle_event_session
            self.battle_event_session = BattleEventSession(config.get('eventURL'), config.get('initBattleURL'), event)
            self.on_session_created(self.battle_event_session)

        elif event.EventName == 'OnBattleResult':
            event_session = None
            if self.battle_event_session.arenaID == arena_id:
                event_session = self.battle_event_session
            if arena_id in self.old_battle_event_sessions:
                event_session = self.old_battle_event_sessions.pop(arena_id)

            if event_session:
                event_session.end_event_session(event)

        else:
            if self.battle_event_session:
                self.battle_event_session.add_event(event)


eventLogger = EventLogger()

def battle_time():
    player = BigWorld.player()

    if not hasattr(player, 'arena'):
        return -10003

    return {
        ARENA_PERIOD.IDLE: -10001,
        ARENA_PERIOD.WAITING: -10000,
        ARENA_PERIOD.PREBATTLE: BigWorld.serverTime() - player.arena.periodEndTime,
        ARENA_PERIOD.BATTLE: BigWorld.serverTime() - eventLogger.start_battle_time,
        ARENA_PERIOD.AFTERBATTLE: BigWorld.serverTime() - eventLogger.start_battle_time
    }.get(player.arena.period, -10002)
