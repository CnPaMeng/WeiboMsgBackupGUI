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
Created on 2012-3-14

@author: Zoe
'''
import wx
import threading
import sys

from model.log4py import Log4py

from model import syscontext
from model.userconfig import UserConfig
import os
from sina.loginsinacom import LoginSinaCom

logger = Log4py().getLogger('LoginThread')

class LoginThread(threading.Thread):
    def __init__(self, threadNum, window, username, password):
        threading.Thread.__init__(self)
        self.threadNum = threadNum
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.username = username
        self.password = password
        self.userConfig = UserConfig(syscontext.userentity["path"])
        #for lock
        self.lock = threading.Lock()
        self.lockcondition=threading.Condition(self.lock)
        
    def stop(self):
        self.timeToQuit.set()
    
    def run(self):
        try:
            syscontext.userentity["un"] = self.username
            syscontext.userentity["pw"] = self.password
            
            loginValid = "ok"
            if loginValid == "ok":
                #login weibo.com to get cookie
                syscontext.MAIN_WINDOW = self.window
                syscontext.MAIN_GENTHREAD = self
                file_path = syscontext.userentity.get("path", "")
                file_path = os.path.join(file_path,
                                         syscontext.FILE_PATH_DEFAULT)
                sina = LoginSinaCom(soft_path=file_path)
                if sina.check_cookie(self.username, self.password, 
                                     file_path):
                    loginValid = "ok"
                else:
                    loginValid = "sina微博登录失败,请检查您的用户名/密码!"
                
            if loginValid == "ok":
                syscontext.LOGIN_SINA_COM = sina
                syscontext.userentity["un"] = self.username
                syscontext.userentity["pw"] = self.password
                logger.info("User:%s login!" % self.username)
            wx.CallAfter(self.window.EnableLoginWin, True)
            wx.CallAfter(self.window.Login, loginValid)
            return None
        except Exception:
            #self.ShowMessage(u"Exception:%s" % str(e), wx.ICON_INFORMATION)
            s=sys.exc_info()
            logger.error(u"Login thread %s happened on line %d" % 
                         (s[1],s[2].tb_lineno))
            #print e
    
