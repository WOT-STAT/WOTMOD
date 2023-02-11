# WIP


from gui.Scaleform.daapi.view.battle.shared import ribbons_aggregator
from helpers import dependency
import BigWorld
from skeletons.gui.battle_session import IBattleSessionProvider
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import _Ribbon, _createRibbonFromPlayerFeedbackEvent

from ..wotHookEvents import wotHookEvents


class OnRibbonsLogger:
  number = 0

  def __init__(self):
    self.number = 0
    wotHookEvents.PlayerAvatar_onEnterWorld += self.on_enter_world

  def on_enter_world(self, *a, **k):
    sessionProvider = dependency.instance(IBattleSessionProvider)
    sessionProvider.shared.feedback.onPlayerFeedbackReceived += self.on_player_feedback_received

  def on_player_feedback_received(self, events):
    for event in events:
      self.number += 1
      event = _createRibbonFromPlayerFeedbackEvent(self.number, event)  # type: _Ribbon
      # print(event.getType())
      # print(event.__slots__)


onRibbonsLogger = OnRibbonsLogger()
