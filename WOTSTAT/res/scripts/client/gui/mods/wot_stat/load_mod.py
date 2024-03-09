# -*- coding: utf-8 -*-
import json

import BigWorld
from .common.config import Config
configPath = './mods/configs/wot_stat/config.cfg'
config = Config(configPath)  # type: Config

from gui import SystemMessages
from .common.modAutoUpdate import update_game_version, update_mod_version
from .common.modNotification import show_notification, OPEN_PERSONAL_WOTSTAT_EVENT
from .common.asyncResponse import get_async

from .utils import print_log
from .logger.wotHookEvents import wotHookEvents
from .logger.sessionStorage import sessionStorage
from .common.serverLogger import setupLogger, send

is_success_check = None
api_server_time = None
is_account_logged_in = False


def mod_name_version(version):
  return 'mod.wotStat_' + version + '.wotmod'


def mod_name():
  return mod_name_version(config.get('version'))


def new_version_found(version):
  print_log('Found new mod version ' + version)


def new_version_update_end(version):
  show_notification(
    '[WotStat] успешно обновлён до версии %s. После перезапуска игры обновление будет применено' % version,
    message_type=SystemMessages.SM_TYPE.Warning)


def on_success_check():
  global is_success_check
  is_success_check = True
  hello_message()


def on_status_check(res):
  global api_server_time, is_success_check

  try:
    data = json.loads(res)
    print_log('Server status: %s' % data)
    api_server_time = data['time']
    hello_message()
  except Exception, e:
    print_log(e)
    api_server_time = None


def on_status_check_fail(e):
  print_log(e)
  show_notification('[WotStat] В данный момент наблюдаются проблемы с сервером WotStat. '
                    'Если проблема будет продолжаться более дня, напишите на почту soprachev@mail.ru',
                    message_type=SystemMessages.SM_TYPE.ErrorSimple)


def on_account_login(*a, **k):
  global is_account_logged_in
  is_account_logged_in = True
  hello_message()
  wotHookEvents.Account_onBecomePlayer -= on_account_login


def on_connected(*a, **k):
  global is_account_logged_in
  if not BigWorld.player():
    wotHookEvents.Account_onBecomePlayer += on_account_login
    is_account_logged_in = False
  else:
    hello_message()


def hello_message():
  global api_server_time, is_success_check, is_account_logged_in
  if (api_server_time is None) or (is_success_check != True) or (is_account_logged_in != True): return

  if not BigWorld.player():
    is_account_logged_in = False
    return

  target_url = 'wotstat.info/session?mode=any&nickname=%s&from=%s' % (BigWorld.player().name, api_server_time)
  print_log(target_url)
  show_notification(
    'WotStat успешно активирован, ваша персональная аналитика за сессию доступна по ссылке <a href="event:%s">%s</a>' % (
      OPEN_PERSONAL_WOTSTAT_EVENT + 'https://' + target_url, target_url),
    message_type=SystemMessages.SM_TYPE.Information)


def init_mod():
  print_log('version ' + config.get('version'))
  setupLogger(config.get('lokiURL'), config.get('version'))

  get_async(config.get('statusURL'), callback=on_status_check, error_callback=on_status_check_fail)
  update_game_version(mod_name())
  update_mod_version(config.get('updateURL'), 'mod.wotStat',
                     config.get('version'),
                     on_start_update=new_version_found,
                     on_updated=new_version_update_end,
                     on_success_check=on_success_check)
  sessionStorage.on_load_mod()
  send("INFO", 'Mod init')


wotHookEvents.onConnected += on_connected
