from Event import Event
from debug_utils import LOG_CURRENT_EXCEPTION
from serverLogger import send_current_exception


def with_exception_sending(f):
  def wrapper(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except:
      send_current_exception()
      LOG_CURRENT_EXCEPTION()

  return wrapper


class SendExceptionEvent(Event):
  __slots__ = ()

  def __init__(self, manager=None):
    super(SendExceptionEvent, self).__init__(manager)

  def __call__(self, *args, **kwargs):
    for delegate in self[:]:
      try:
        delegate(*args, **kwargs)
      except:
        send_current_exception()
        LOG_CURRENT_EXCEPTION()
