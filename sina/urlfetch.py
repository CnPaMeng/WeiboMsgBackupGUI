#!/usr/bin/python
#-*- encoding: utf-8 -*-

# This file is part of the Pameng, 
# Pameng website: http://www.cnpameng.com/,
# Sina weibo: http://weibo.com/cnpameng.

# This file is part of WeiboMsgBackup.

# Copyright (C) 2013 Pameng.
# Pameng <pameng.cn@gmail.com>, 2013.

# WeiboMsgBackup is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# WeiboMsgBackup is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with WeiboMsgBackup; see the file COPYING3.  If not see
# <http://www.gnu.org/licenses/>.


import httplib
import socket
import urllib
import urlparse
from uas import randua


def setcookie2cookie(setcookie):
    cookies = setcookie.split("\n")
    result = []
    for ck in cookies:
        frags = ck.split(";")
        i = frags[0].index("=")
        name = frags[0][:i]
        value = frags[0][i+1:]
        #name = name.replace("+", " ")
        if name.strip():
            result.append([name, value])
    return result


def setcookielist2cookiestring(cookie):
    cookies = []
    for i in cookie:
        cookies.extend(setcookie2cookie(i))
    cookiestring = "; ".join(["%s=%s" % (name, value) for name, value in cookies])
    return cookiestring


def setcookie2cookiestring(setcookie):
    cookies = setcookie2cookie(setcookie)
    return '; '.join(['%s=%s' % (name, value) for name, value in cookies])


def fetch(url, data=None, headers={}, timeout=None):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    
    if ':' in netloc:
        host, port = netloc.rsplit(':', 1)
        port = int(port)
    else:
        host, port = netloc, 80
    
    h = httplib.HTTPConnection(host, port)
    if timeout is not None:
        h.connect()
        h.sock.settimeout(timeout)
    
    reqheaders = {
        'Accept' : '*/*',
        'User-Agent': randua(),
    }
    
    if data is not None and isinstance(data, (basestring, dict)):
        method = "POST"
        reqheaders["Content-Type"] = "application/x-www-form-urlencoded"
        # httplib will set 'Content-Length', also you can set it by yourself
        if isinstance(data, dict):
            data = urllib.urlencode(data)
    else:
        method = "GET"
        
    reqheaders.update(headers)
    
    h.request(method, url, data, reqheaders)
    response = h.getresponse()
    setattr(response, 'reqheaders', reqheaders)
    setattr(response, 'body', response.read())
    h.close()
    
    return response


def fetch2(url, method="GET", data=None, headers={}, timeout=None):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    method = method.upper()
    if method not in ("GET", "PUT", "DELETE", "POST", "HEAD"):
        method = "GET"
    
    if ':' in netloc:
        host, port = netloc.rsplit(':', 1)
        port = int(port)
    else:
        host, port = netloc, 80
    
    h = httplib.HTTPConnection(host, port)
    if timeout is not None:
        h.connect()
        h.sock.settimeout(timeout)
    
    reqheaders = {
        'Accept' : '*/*',
        'User-Agent': randua(),
    }
    
    if method == "POST" and data is not None and isinstance(data, (basestring, dict)):
        reqheaders["Content-Type"] = "application/x-www-form-urlencoded"
        # httplib will set 'Content-Length', also you can set it by yourself
        if isinstance(data, dict):
            data = urllib.urlencode(data)
        
    reqheaders.update(headers)
    
    h.request(method, url, data, reqheaders)
    response = h.getresponse()
    setattr(response, 'reqheaders', reqheaders)
    setattr(response, 'body', response.read())
    h.close()
    
    return response


if __name__ == '__main__':
    import sys
    url = sys.argv[1]
    response = fetch(url, data='test')
    print 'request headers', response.reqheaders
    print 'response headers', response.getheaders()
    print 'body length', len(response.body)