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


import sys
import urllib2
import StringIO
import gzip
import urllib
import time
import datetime
import cookielib
from model.log4py import Log4py

cj = cookielib.CookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

logger = Log4py().getLogger('run')


def setCookie(cookie):
    cj.set_cookie(cookie)


def getMillitime():
    pre = str(int(time.time()))
    pos = str(datetime.datetime.now().microsecond)[:3]
    p = pre + pos
    return p


def gzipData(spiderData):
    if 0 == len(spiderData):
        return spiderData
    spiderDataStream = StringIO.StringIO(spiderData)
    spiderData = gzip.GzipFile(fileobj=spiderDataStream).read()
    return spiderData


def getHtmlSource(url, headers={}, data={}, proxyip=""):
    content = ""
    try:
        if not url.startswith("http://"):
            url = "http://" + url
        request = urllib2.Request(url=url.strip(), headers=headers)
        #data is a dict type:{key:val}
        if data:
            logger.info("Add post data.")
            request.add_data(urllib.urlencode(data))
        #opener = None
        if proxyip and "127.0.0.1" not in proxyip:
            if not proxyip.startswith("http"):
                proxyip = "http://" + proxyip
            #print proxyip
            proxy_handler = urllib2.ProxyHandler({'http': proxyip})
            #opener.add_handler(proxy_handler)
            opener = urllib2.build_opener(cookie_support, proxy_handler) 
        else:
            opener = urllib2.build_opener(cookie_support)
        response = opener.open(request, timeout=10)
        if response.info().get("Content-Encoding") == 'gzip':
            content = gzipData(response.read())
        else:
            content = response.read()
        if "抱歉，你的帐号存在异常，暂时无法访问" in content and "解除限制" in content:
            content = ""
    except:
        s = sys.exc_info()
        msg = (u"ip:%s getHtmlSource Error %s happened on line %d" % (proxyip, s[1], s[2].tb_lineno))
        logger.error(msg)
        logger.error(url)
    return content


def getHtmlAutoRedirect(url, headers={}, data={}, proxyip=""):
    code = 0
    content = ""
    try:
        if not url.startswith("http://"):
            url = "http://"+url
        request = urllib2.Request(url=url.strip(), headers=headers)
        #data is a dict type:{key:val}
        if data:
            logger.info("Add post data.")
            request.add_data(urllib.urlencode(data))
        if proxyip and "127.0.0.1" not in proxyip:
            if proxyip.startswith("http"):
                proxyip = proxyip.replace("http://", "")
            request.set_proxy(proxyip, "http")
        try:
            response = urllib2.urlopen(request, timeout=10)
            code = response.getcode()
        except urllib2.HTTPError, e:
            code = e.code
            return code,content
        if response.info().get("Content-Encoding") == 'gzip':
            content = gzipData(response.read())
        else:
            content = response.read()
        if "抱歉，你的帐号存在异常，暂时无法访问" in content and "解除限制" in content:
            content = ""
    except:
        s = sys.exc_info()
        msg = (u"ip:%s getHtmlSource Error %s happened on line %d" % (proxyip, s[1], s[2].tb_lineno))
        logger.error(msg)
        logger.error(url)
    return code,content
