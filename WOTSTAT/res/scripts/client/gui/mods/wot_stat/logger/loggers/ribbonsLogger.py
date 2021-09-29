# WIP


from gui.Scaleform.daapi.view.battle.shared import ribbons_aggregator
from helpers import dependency
import BigWorld
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import _createRibbonFromPlayerFeedbackEvent


# #evnt = None
# def onPlayerFeedbackReceived(events):
#     global evnt
#     evnt = events
#     print(events)

# #sessionProvider = dependency.instance(IBattleSessionProvider)
# #sessionProvider.shared.feedback.onPlayerFeedbackReceived += onPlayerFeedbackReceived

# #print(evnt[0].getExtra().isRam())
# #t = _createRibbonFromPlayerFeedbackEvent(1, evnt[0])
# print(BigWorld.player().arena.vehicles[t.getVehicleID()])