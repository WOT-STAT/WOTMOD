

def readClientServerVersion():
  try: 
    from account_shared import readClientServerVersion
    return readClientServerVersion()
  
  except ImportError:
    from version_utils import readClientServerVersion
    from helpers import clientVersionGetter
    from constants import AUTH_REALM
    req, ver = readClientServerVersion(clientVersionGetter)
    if len(ver.split('#')) == 2: ver = ver.split('#')[0]
    
    
    prefix = ''
    
    try:
      from realm import CURRENT_REALM, IS_CT
      if CURRENT_REALM == 'RU' and IS_CT: prefix = 'rpt_'
      if CURRENT_REALM == 'RU' and not IS_CT: prefix = 'ru_'
    except ImportError:
      pass   
    
    if AUTH_REALM == 'CT' and prefix == '': prefix = 'ct_'
    return (req, prefix + ver)