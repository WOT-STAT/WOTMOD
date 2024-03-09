import hashlib
import json
import os
import sys
import time
from traceback import format_exception

from typing import List

import BigWorld
import excepthook
from account_shared import readClientServerVersion
from constants import AUTH_REALM
from debug_utils import _addTagsToMsg, _makeMsgHeader, LOG_CURRENT_EXCEPTION, _src_file_trim_to, _g_logLock
from .common.asyncResponse import post_async

logger = None  # type: ServerLogger
modVersion = 'unknown'

GAME_VERSION = readClientServerVersion()[1]


def setupLogger(url, version):
  global logger, modVersion
  modVersion = version
  logger = ServerLogger(url)


def send(level, msg):
  if logger:
    logger.send(level, msg)
  else:
    print("[WOTSTAT] LOGGER ERROR. Call before init")


def send_current_exception(tags=None, frame=1):
  msg = _makeMsgHeader(sys._getframe(frame)) + '\n'
  etype, value, tb = sys.exc_info()
  msg += ''.join(format_exception(etype, value, tb, None))
  with _g_logLock:
    line = ''
    line += '[EXCEPTION]' + _addTagsToMsg(tags, msg)
    extMsg = excepthook.extendedTracebackAsString(_src_file_trim_to, None, None, etype, value, tb)
    if extMsg:
      line += '[EXCEPTION]' + _addTagsToMsg(tags, extMsg)

  send(LEVELS.ERROR, line)


def withExceptionHandling(l):
  try:
    l()
  except:
    send_current_exception()
    LOG_CURRENT_EXCEPTION()


def _generate_session_id():
  current_time = str(time.time()).encode('utf-8')
  random_bytes = os.urandom(16)
  unique_bytes = current_time + random_bytes
  session_id = hashlib.sha256(unique_bytes).hexdigest()

  return session_id


def _get_player_name():
  player = BigWorld.player()

  if not player: return 'unknown_player'
  if not player.name: return 'unknown_name'
  return player.name


def _get_game_version():
  if not GAME_VERSION: return 'unknown_version'
  return GAME_VERSION


def _get_mod_version():
  return modVersion


def _get_region():
  return AUTH_REALM


class LEVELS:
  DEBUG = 'DEBUG'
  INFO = 'INFO'
  WARN = 'WARN'
  ERROR = 'ERROR'


LEVELS_NAMES = [LEVELS.DEBUG, LEVELS.INFO, LEVELS.WARN, LEVELS.ERROR]


class Message:
  def __init__(self, level, message):
    self.level = level if level in LEVELS_NAMES else LEVELS.INFO
    self.message = message if message else "empty"
    self.time = int(time.time() * 1e9)


def _on_send_error(res):
  print('[WOTSTAT LOGGER] sending error')
  print(res)


class ServerLogger:
  session_id = _generate_session_id()
  logs_queue = []  # type: List[Message]

  def __init__(self, url):
    self.url = url
    print("[WOTSTAT LOGGER]: Init server logger to: %s", self.url)
    self._sending_loop()

  def send(self, level, msg):
    self.logs_queue.append(Message(level, msg))

  def _sending_loop(self):
    BigWorld.callback(5, self._sending_loop)

    try:
      if len(self.logs_queue) == 0: return

      defaultStreamMeta = {
        "service": "mod",
        "playerName": _get_player_name(),
        "region": _get_region(),
        "gameVersion": _get_game_version(),
        "modVersion": _get_mod_version(),
        "session": self.session_id
      }

      streams = []

      for level in LEVELS_NAMES:
        current = filter(lambda l: l.level == level, self.logs_queue)
        if len(current) == 0: continue

        streams.append({
          "stream": dict(defaultStreamMeta, level=level),
          "values": map(lambda l: [str(l.time), l.message], current)
        })

      data = {"streams": streams}

      send_data = json.dumps(data, ensure_ascii=False)
      post_async(self.url, data=send_data, error_callback=_on_send_error)

    except:
      print("[WOTSTAT LOGGER EXCEPTION]")
      LOG_CURRENT_EXCEPTION()

    finally:
      self.logs_queue = []
