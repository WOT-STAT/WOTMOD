# -*- coding: utf-8 -*-
from helpers import getClientLanguage

RU = {
  "modUpdated": "[WotStat] успешно обновлён до версии %s. После перезапуска игры обновление будет применено",
  "serverNotResponse": "[WotStat] В данный момент наблюдаются проблемы с сервером WotStat. Если проблема будет продолжаться более дня, напишите на почту soprachev@mail.ru",
  "modslist.title": "WotStat Аналитика",
  "modslist.description": "Просмотр персональной аналитики WotStat за текущую сессию",
  "helloNotification": "WotStat успешно активирован, ваша персональная аналитика за сессию доступна по ссылке <a href=\"event:%s\">%s</a>",
  "openDialog.title": "WotStat Аналитика",
  "openDialog.body": "Персональная сессионная аналитика откроется в браузере по умолчанию.\n\nНовые события в сессии подгружаются автоматически.",
  "openDialog.cancelButton": "Отмена",
  "openDialog.openButton": "Открыть в браузере"
}

EN = {
  "modUpdated": "[WotStat] successfully updated to version %s. The update will be applied after restarting the game.",
  "serverNotResponse": "[WotStat] Currently experiencing issues with the WotStat server. If the problem persists for more than a day, please write to soprachev@mail.ru",
  "modslist.title": "WotStat Analytics",
  "modslist.description": "View your WotStat personal analytics for the current session",
  "helloNotification": "WotStat successfully activated, your session personal analytics are available at <a href=\"event:%s\">%s</a>",
  "openDialog.title": "WotStat Analytics",
  "openDialog.body": "Your session personal analytics will open in the default browser.\n\nNew session events are automatically loaded.",
  "openDialog.cancelButton": "Cancel",
  "openDialog.openButton": "Open in browser"
}
language = getClientLanguage()
current_localizations = RU

if language == 'ru':
  current_localizations = RU
else:
  current_localizations = EN


def t(key):
  if key in current_localizations:
    return current_localizations[key]
  return key
