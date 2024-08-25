import BigWorld

from battleEventSession import BattleEventSession, HangarEventSession
from constants import ARENA_PERIOD
from events import Event
from ..common.exceptionSending import SendExceptionEvent
from ..utils import print_debug
from ..load_mod import config

from ..thirdParty.dataProviderExtension import triggerEvent

class EventLogger:
  old_battle_event_sessions = {}
  battle_event_session = None  # type: BattleEventSession
  start_battle_time = 0
  on_session_created = SendExceptionEvent()
  hangar_event_session = HangarEventSession(config.get('eventURL'))

  def __init__(self):
    print_debug('INIT EVENT LOGGER')

  def emit_event(self, event, arena_id=None):
    if event.eventName == Event.NAMES.ON_BATTLE_START:
      if self.battle_event_session:
        self.old_battle_event_sessions[self.battle_event_session.arenaID] = self.battle_event_session
      self.battle_event_session = BattleEventSession(config.get('eventURL'), config.get('initBattleURL'), event)
      self.on_session_created(self.battle_event_session)

    elif event.eventName == Event.NAMES.ON_BATTLE_RESULT:
      event_session = None
      if self.battle_event_session.arenaID == arena_id:
        event_session = self.battle_event_session
      if arena_id in self.old_battle_event_sessions:
        event_session = self.old_battle_event_sessions.pop(arena_id)

      if event_session:
        event_session.end_event_session(event)

    elif event.eventName in Event.NAMES.HANGAR_EVENTS:
      self.hangar_event_session.add_event(event)

    else:
      if self.battle_event_session:
        self.battle_event_session.add_event(event)

    triggerEvent(event.get_dict())

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
