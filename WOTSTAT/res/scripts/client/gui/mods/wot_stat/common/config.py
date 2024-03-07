# coding=utf-8

import json
import os
import BigWorld
from gui import SystemMessages
from ..utils import print_log
from .modNotification import show_notification


class Config:
  config = {}
  defaultParams = {
    'version': '0.0.0.0',
    'initBattleURL': 'https://wotstat.info/api/events/OnBattleStart',
    'eventURL': 'https://wotstat.info/api/events/send',
    'updateURL': 'https://api.github.com/repos/WOT-STAT/WOTMOD/releases/latest',
    'statusURL': 'https://wotstat.info/api',
    'lokiURL': 'https://loki.wotstat.info/loki/api/v1/push',
    'hideServer': False
  }

  def __init__(self, ConfigPath, DefaultParams=None):
    self.config = {}
    if DefaultParams:
      self.defaultParams = DefaultParams

    if os.path.exists(ConfigPath):
      with open(ConfigPath, "r") as f:
        try:
          self.config = json.loads(f.read())
          print_log('found new config:')
          print_log(self.config)
          config_str = '''\n------\n'''.join("%s: %s" % (key, value) for key, value in self.config.items())

          message = '''[WotStat] Обнаружена новая конфигурация в файле /mods/configs/wot_stat/config.cfg\n------\n%s''' % config_str

          BigWorld.callback(5.0, lambda: show_notification(message, message_type=SystemMessages.SM_TYPE.Warning))
        except Exception, e:
          print_log('load config error')
          print_log(e)

    try:
      # noinspection PyUnresolvedReferences
      self.config['version'] = version
    except Exception, e:
      pass

  def get(self, key):
    return self.config[key] if key in self.config else self.defaultParams[
      key] if key in self.defaultParams else None
