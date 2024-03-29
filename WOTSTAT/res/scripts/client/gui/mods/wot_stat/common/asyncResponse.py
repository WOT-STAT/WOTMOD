import BigWorld

import threading
import urllib2
import ssl

json_headers = {'Content-type': 'application/json',
                'Accept': 'application/json'}


def get_async(url, data=None, callback=None, headers=None, error_callback=None):
  request_async(url, data, headers, get, callback, error_callback)


def post_async(url, data=None, callback=None, headers=None, error_callback=None):
  request_async(url, data, headers, post, callback, error_callback)


def request_async(url, data, headers, method, callback, error_callback=None):
  event = threading.Event()
  runner = threading.Thread(target=run,
                            args=(event, url, data, headers, method, callback, error_callback))
  runner.start()
  event.wait()


def run(event, url, data, headers, method, callback, error_callback):
  event.set()
  try:
    result = method(url, data, headers)
    if callback:
      callback(result)
  except Exception, e:
    if error_callback:
      error_callback(e)
    else:
      raise e


def get(url, data, headers):
  context = ssl._create_unverified_context()
  if data:
    params = urllib2.urlencode(data)
    url = '?'.join(url, params)
  if headers:
    req = urllib2.Request(url, headers=headers)
    return urllib2.urlopen(req, context=context).read()
  else:
    return urllib2.urlopen(url, context=context).read()


def post(url, data, headers):
  context = ssl._create_unverified_context()
  if data:
    req = urllib2.Request(url, data, headers=json_headers)
    return urllib2.urlopen(req, context=context).read()
  else:
    return urllib2.urlopen(url, context=context).read()
