import BigWorld
from ..utils import print_log
from typing import List

# typing for intellisense
class ITrigger(object):
  def trigger(self, value=None): pass
  
class IState(object):
  def getValue(self): pass
  def setValue(self, value): pass
  
class IExtension(object):
  def createState(self, path, initialValue = None):
    # type: (List[str], any) -> IState
    pass
  
  def createTrigger(self, path):
    # type: (List[str]) -> ITrigger
    pass
  
class IDataProviderSDK(object):
  version = None # type: int
  def registerExtension(self, name):
    # type: (str) -> IExtension
    pass
  
  
onEventTrigger = None # type: ITrigger

def triggerEvent(event):
  if onEventTrigger:
    onEventTrigger.trigger(event)

def setupExtension():
  global onEventTrigger
  
  if not hasattr(BigWorld, 'wotstat_dataProvider'):
    return
  
  provider = BigWorld.wotstat_dataProvider # type: IDataProviderSDK
  
  providerVersion = provider.version
  extension = provider.registerExtension('wotstat')
  onEventTrigger = extension.createTrigger(['onEvent'])
  
  print_log('Extension setup complete. Data provider version: %s' % str(providerVersion))


BigWorld.callback(0.1, setupExtension)