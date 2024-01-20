import json
import os
import BigWorld
from ..utils import print_log


class Config:
  config = {}
  defaultParams = {
    'version': '0.0.0.0',
    'initBattleURL': 'https://dev.wotstat.soprachev.com/api/events/OnBattleStart',
    'eventURL': 'https://dev.wotstat.soprachev.com/api/events/send',
    'updateURL': 'https://api.github.com/repos/WOT-STAT/WOTMOD/releases/latest',
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


Config = Config
