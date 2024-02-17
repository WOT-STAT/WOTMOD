# -*- coding: utf-8 -*-
import BigWorld
import json

from gui import SystemMessages
from .common.config import Config
from .common.modAutoUpdate import update_game_version, update_mod_version
from .common.modNotification import show_notification, OPEN_PERSONAL_WOTSTAT_EVENT
from .common.asyncResponse import get_async
from .utils import print_log

configPath = './mods/configs/wot_stat/config.cfg'
config = Config(configPath)  # type: Config
from .logger.eventLogger import eventLogger
from .logger.wotHookEvents import wotHookEvents

is_success_check = None
api_server_time = None
is_account_logined = False


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
  global is_account_logined
  is_account_logined = True
  wotHookEvents.Account_onBecomePlayer -= on_account_login
  hello_message()


def hello_message():
  global api_server_time, is_success_check
  if (api_server_time is None) or (is_success_check != True) or (is_account_logined != True): return

  target_url = 'wotstat.info/session?mode=any&nickname=%s&from=%s' % (BigWorld.player().name, api_server_time)
  print_log(target_url)
  show_notification(
    'WotStat успешно активирован, ваша персональная аналитика за сессию доступна по ссылке <a href="event:%s">%s</a>' % (
      OPEN_PERSONAL_WOTSTAT_EVENT + 'https://' + target_url, target_url),
    message_type=SystemMessages.SM_TYPE.Information)


def init_mod():
  global logger

  print_log('version ' + config.get('version'))

  get_async(config.get('statusURL'), callback=on_status_check, error_callback=on_status_check_fail)
  update_game_version(mod_name())
  update_mod_version(config.get('updateURL'), 'mod.wotStat',
                     config.get('version'),
                     on_start_update=new_version_found,
                     on_updated=new_version_update_end,
                     on_success_check=on_success_check)


wotHookEvents.Account_onBecomePlayer += on_account_login
