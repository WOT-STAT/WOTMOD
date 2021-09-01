# -*- coding: utf-8 -*-

import BigWorld

import threading
import urllib2

json_headers = {'Content-type': 'application/json',
                'Accept': 'application/json'}


def get_async(url, data=None, callback=None):
    request_async(url, data, get, callback)


def post_async(url, data=None, callback=None):
    request_async(url, data, post, callback)


def request_async(url, data, method, callback):
    event = threading.Event()
    runner = threading.Thread(target=run,
                              args=(event, url, data, method, callback))
    runner.start()
    event.wait()


def run(event, url, data, method, callback):
    event.set()
    result = method(url, data)
    if callback:
        callback(result)


def get(url, data):
    if data:
        params = urllib2.urlencode(data)
        url = '?'.join(url, params)
    return urllib2.urlopen(url).read()


def post(url, data):
    if data:
        req = urllib2.Request(url, data, headers=json_headers)
        return urllib2.urlopen(req).read()
    else:
        return urllib2.urlopen(url).read()
