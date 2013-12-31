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

from model.crawlerthread import CrawlerThread

from model.loginthread import LoginThread

from model.log4py import Log4py
from model.usersearchcom import UserSearchThread
logger = Log4py().getLogger('run')

class MainAction():
    
    def _init__(self):
        pass
    
    def Login(self,window, username, password):
        thread = LoginThread(1, window, username, password)#创建一个线程
        thread.start()#启动线程
        thread.stop()
    
    def StartCrawler(self, window):
        self.SetCrawlerTaskData(window.taskPath, 'gsid', 
                                           window.slider.GetValue(), 
                                           window.CRAWLER_TYPE, window)
        self.Crawler()
            
                
    def SetCrawlerTaskData(self, taskPath=None,
                           gsid=None,
                           threadNum=10,
                           _type=0,
                           window=None
                           ):
        self.window = window
        crawlerData = {}
        crawlerData["taskPath"] = taskPath
        crawlerData["resultPath"] = window.resultPath
        crawlerData["gsid"] = gsid
        crawlerData["threadNum"] = threadNum
        crawlerData["type"] = _type
        self.crawlerData = crawlerData
        self.threadNum = threadNum
#        print 'crawlerData:',self.crawlerData
        
    def Crawler(self):
        #创建一个线程
        thread = CrawlerThread(self.threadNum, self.crawlerData, self.window)
        self.window.threads.append(thread)
        #启动线程
        thread.start()
        
    '''
    #搜索sina微博用户
    '''
    def SearchWeibocnUser(self, searchName, window):
        userSearch = UserSearchThread(searchName, window)
        userSearch.start()
        userSearch.join()
        