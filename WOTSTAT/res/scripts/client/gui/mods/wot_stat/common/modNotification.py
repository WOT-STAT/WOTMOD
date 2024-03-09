# coding=utf-8
import BigWorld
from gui import SystemMessages
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta
from notification.actions_handlers import NotificationsActionsHandlers
from .exceptionSending import with_exception_sending
from ..utils import print_log


OPEN_PERSONAL_WOTSTAT_EVENT = 'OPEN_PERSONAL_WOTSTAT_EVENT_'


class UrlDialogButtons(object):
  def getLabels(self):
    return [
      {'id': DIALOG_BUTTON_ID.SUBMIT, 'label': 'Открыть в браузере', 'focused': True},
      {'id': DIALOG_BUTTON_ID.CLOSE, 'label': 'Отмена', 'focused': False}
    ]


@with_exception_sending
def show_url_dialog(title=None, message=None, url=None):
  meta = SimpleDialogMeta(title=title, message=message, buttons=UrlDialogButtons())
  showDialog(meta, lambda proceed: BigWorld.wg_openWebBrowser(url) if proceed else None)


@with_exception_sending
def __wotstat_events_handleAction(self, model, typeID, entityID, actionName):
  try:
    if actionName.startswith(OPEN_PERSONAL_WOTSTAT_EVENT):
      target = actionName.split(OPEN_PERSONAL_WOTSTAT_EVENT)[1]
      show_url_dialog('Аналитика WotStat',
                      'Персональная сессионная аналитика откроется в браузере по умолчанию. ' +
                      '''\n\nНовые события в сессии подгружаются автоматически.''',
                      target)
    else:
      old_handleAction(self, model, typeID, entityID, actionName)
  except:
    old_handleAction(self, model, typeID, entityID, actionName)


old_handleAction = NotificationsActionsHandlers.handleAction
NotificationsActionsHandlers.handleAction = __wotstat_events_handleAction


@with_exception_sending
def show_notification(msg, message_type=SystemMessages.SM_TYPE.Information):
  print_log('show notification: %s. With type: %s' % (msg, message_type))
  SystemMessages.pushMessage(msg, type=message_type)
