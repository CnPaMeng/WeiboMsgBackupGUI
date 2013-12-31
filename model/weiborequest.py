#!/usr/bin/python
#-*- encoding: utf-8 -*-

# This file is part of the Pameng, 
# Pameng website: http://www.cnpameng.com/,
# Sina weibo: http://weibo.com/cnpameng.
#
# This file is part of WeiboMsgBackup.
#
# Copyright (C) 2013 Pameng.
# Pameng <pameng.cn@gmail.com>, 2013.
#
# WeiboMsgBackup is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# WeiboMsgBackup is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WeiboMsgBackup; see the file COPYING3.  If not see
# <http://www.gnu.org/licenses/>.


 
'''
Created on 2012-2-15

@author: Zoe
for m.weibo.cn
'''

import sys
from model.log4py import Log4py
logger = Log4py().getLogger('run')

class WeiboRequest():
    
    def __init__(self, uid, sina):
        self.uid = uid
        self.sina = sina
        
    def getLoginUserInfo(self):
        user = {}
        try:
            url = "http://weibo.com"
            headers = {'Host':'weibo.com',
                       'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1',
                       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                       'Accept-Encoding':'gzip, deflate',
                       'Connection':'keep-alive',
                      }
            html = self.sina.get_content_head(url, headers)
            if '用户不存在哦!' in html:
                #print (u'weibo用户不存在!')
                return None
            if '您当前访问的用户状态异常' in html:
                #print (u'weibo用户状态异常!')
                return None
            #user base info
            if html:
                
                sindex = html.find("$CONFIG['uid']")
                uid = html[sindex: html.find("';", sindex)]
                #uid
                user["uid"] = uid.replace("$CONFIG['uid']", '').replace('=', '').replace("'", '').strip()
                #nick
                sindex = html.find("$CONFIG['nick']")
                nick = html[sindex: html.find("';", sindex)]
                user["sn"] = nick.replace("$CONFIG['nick']", '').replace('=', '').replace("'", '').strip()
            else:
                return None
        except Exception:
            s=sys.exc_info()
            msg = (u"parse user basic info Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
            return None
        return user
    
    def stop(self):
        self.timeToQuit.set()
    
if __name__ == '__main__':
    print 'start.'
