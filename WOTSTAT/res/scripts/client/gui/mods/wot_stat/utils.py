import BigWorld

def print_log(log):
    print("%s [MOD_WOT_STAT]: %s" % (BigWorld.serverTime(), str(log)))

def print_debug(log):
    print("%s [MOD_WOT_STAT DEBUG]: %s" % (BigWorld.serverTime(), str(log)))