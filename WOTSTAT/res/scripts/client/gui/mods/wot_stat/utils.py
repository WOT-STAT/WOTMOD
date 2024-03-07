import BigWorld
from .serverLogger import send, LEVELS


def print_log(log):
  print("%s [MOD_WOT_STAT]: %s" % (BigWorld.serverTime(), str(log)))
  send(LEVELS.INFO, str(log))


def print_debug(log):
  if DEBUG_MODE:
    print("%s [MOD_WOT_STAT DEBUG ]: %s" % (BigWorld.serverTime(), str(log)))
