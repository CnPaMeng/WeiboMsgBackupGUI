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
from model.mainaction import MainAction

logger = Log4py().getLogger('StartCrawlThread')

class StartCrawlThread(threading.Thread):
    """
    This just simulates some long-running task that periodically sends
    a message to the GUI thread.
    """
    def __init__(self, threadNum, window, event):
        threading.Thread.__init__(self)
        self.threadNum = threadNum
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.userConfig = UserConfig(syscontext.userentity["path"])
        self.event = event
        self.mainAction = MainAction()
        
    def stop(self):
        self.timeToQuit.set()
    
    def run(self):#运行一个线程
        try:
            if self.window.CRAWLER_STATUS == 0:
                if self.event is None:
                    self.window.crawlerCount += 1
                msg = u"====开启第 %d 次采集====" % self.window.crawlerCount
                wx.CallAfter(self.window.WriteLog, msg)
                logger.info(msg)
                wx.CallAfter(self.window.ReInit)
                #self.userConfig.WriteUserConfig("sinauser", self.window.webUNText.GetValue().strip())
                #结果路径配置信息
                savePath = self.window.savePathText.GetValue().strip()
                if savePath == "":
                    savePath = self.window.taskPath
                self.window.resultPath = savePath
                self.userConfig.WriteUserConfig("save", self.window.savePathText.GetValue().strip())
                self.mainAction.StartCrawler(self.window)
            else:
                wx.CallAfter(self.window.OnCrawlerStop, None)
            return None
        except Exception:
            #self.ShowMessage(u"Exception:%s" % str(e), wx.ICON_INFORMATION)
            s=sys.exc_info()
            logger.error(u"StartCrawlThread thread %s happened on line %d" % (s[1],s[2].tb_lineno))
            msg = u"开启采集失败!case" % s[1]
            wx.CallAfter(self.window.WriteLog, msg)
    
