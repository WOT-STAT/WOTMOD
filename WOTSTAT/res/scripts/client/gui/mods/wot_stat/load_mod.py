# -*- coding: utf-8 -*-
import BigWorld

from gui import SystemMessages

from .common.config import Config
from .common.modAutoUpdate import update_game_version, update_mod_version
from utils import print_log

configPath = './mods/configs/wot_stat/config.cfg'
config = Config(configPath)  # type: Config
from .logger.eventLogger import EventLogger


logger = None


def mod_name_version(version):
    return 'mod.wotStat_' + version + '.wotmod'


def mod_name():
    return mod_name_version(config.get('version'))


def init_mod():
    global logger

    print_log('version ' + config.get('version'))

    update_game_version(mod_name())
    update_mod_version('https://wotstat.soprachev.com/cache/mod/version', 'mod.wotStat', config.get('version'),
                       on_start_update=lambda t: print_log(
                           'Found new mod version ' + t),
                       on_updated=lambda t: SystemMessages.pushMessage(
                           '[WotStat] успешно обновлён до версии ' + t +
                           '. После перезапуска игры обновление будет применено',
                           type=SystemMessages.SM_TYPE.Warning))

    logger = EventLogger()


