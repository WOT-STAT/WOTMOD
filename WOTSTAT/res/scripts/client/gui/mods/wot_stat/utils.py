import BigWorld


def print_log(log):
  print("%s [MOD_WOT_STAT_DEV]: %s" % (BigWorld.serverTime(), str(log)))


def print_debug(log):
  print("%s [MOD_WOT_STAT_DEV DEBUG ]: %s" % (BigWorld.serverTime(), str(log)))
