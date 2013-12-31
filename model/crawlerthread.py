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

from __future__ import division
import wx
import threading
import os
import time
import sys
from Queue import Queue, Empty
import workerpool
import csv
from model.userentity import * #@UnusedWildImport
from model.msgentity import * #@UnusedWildImport

from model.log4py import Log4py
from model import syscontext
from model.weiborequest import WeiboRequest
from model.msgcomcrawlerthread import MsgComCrawlerThread

logger = Log4py().getLogger('run')

class CrawlerThread(threading.Thread):
    """
    This just simulates some long-running task that periodically sends
    a message to the GUI thread.
    """
    def __init__(self, threadNum, crawlerData, window):
        threading.Thread.__init__(self)
        self.threadNum = threadNum
        self.crawlerData = crawlerData
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        #threadNum: 1
        self.pool = workerpool.WorkerPool(1)
        self.count = 1;
        
    def stop(self):
        self.timeToQuit.set()
        
    #运行一个线程
    def run(self):
        self.window.CRAWLER_STATUS = 1
        msg = ""
        crawlerData = self.crawlerData
        output_path = crawlerData["resultPath"]
        try:
            task_info = {}
            now = time.time()
            uids = []
            if self.window.CRAWLER_SELF:
                self.window.CRAWLER_SELF = 0
                userSearch = WeiboRequest("", syscontext.LOGIN_SINA_COM)
                loginUser = userSearch.getLoginUserInfo()
                if loginUser:
                    wx.CallAfter(self.window.WriteLog,
                                 u"选定采集用户：%s" % loginUser.get("sn"))
                    uids.append(loginUser.get("uid"))
                else:
                    uids = []
                    msg = u"获取当前登录用户信息失败：  %s" % loginUser
                    wx.CallAfter(self.window.WriteLog, msg)
                    logger.error(msg)
                    return None
            else:
                if syscontext.tempentity.get("CRAWLERUID", None):
                    uids.extend(syscontext.tempentity.get("CRAWLERUID"))
            task_info["gsid"] = [crawlerData["gsid"]]
            logger.info("workerpool size:%d" % self.threadNum)
            q = Queue(0) 
            
            msg = u"需执行的任务数：  %d" % len(uids)
            wx.CallAfter(self.window.WriteLog, msg)
            msg = "please wait..."
            wx.CallAfter(self.window.WriteLog, msg)
            logger.info(u"创建线程 SIZE  %d" % len(uids))
            
            for i in range(len(uids)):
                job = MsgComCrawlerThread(q, uids[i], task_info, i, 
                                          self.window, self.threadNum, 
                                          output_path, proxylist=[])
                self.pool.put(job)
                
            self.pool.shutdown()
            self.pool.wait()
            
            result_list = []
            try:
                for i in range(q.qsize()):
                    result_list.append(q.get(block=False))
            except Empty:
                pass # Success
            msg = "================"
            wx.CallAfter(self.window.WriteLog, msg)
            elapsed = time.time() - now
            logger.info("Current reqCount %d / Total reqCount %d" %
                        (self.window.curCount,self.window.totalCount))
            msg = u'耗时 : %ds 发送请求: %d' % (int(elapsed),
                                          int(self.window.totalCount))
            logger.info(u"耗时 : %ds 发送请求: %d" % (int(elapsed),
                                                int(self.window.totalCount)))
            wx.CallAfter(self.window.WriteLog, msg)
            
            '''
            #返回数据中包含 user 和 msg
            '''
            userLst = []
            msgLst = []
            for re in result_list:
                userLst.append(re.get("user"))
                msgLst.extend(re.get("msg"))
                
            t = time.strftime( '%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
            self.CopyResultDat2Csv(output_path, str(t), userLst)

            msg = (u'结果写入：%s' % output_path)
            wx.CallAfter(self.window.WriteLog, msg)
            logger.info(u"Write Result: %s with size: %d"%(output_path,
                                                           len(msgLst)))
            
            self.window.CRAWLER_STATUS = 0
            wx.CallAfter(self.window.UpdateCrawlProcess, 
                         int(self.window.totalCount)*2+27)
            wx.CallAfter(self.window.ThreadFinished, self)
            logger.info("本次采集完成!")
            logger.info("END crawler thread!")
            
        except Exception, e:
            wx.CallAfter(self.window.ThreadFinished, self)
            wx.CallAfter(self.window.WriteLog, u'采集Exception: %s'+str(e))
            logger.error(u"采集Exception: %s" % str(e))
            
        finally:
            wx.CallAfter(self.window.UpdateBtnLabel, u"开始采集")
            wx.CallAfter(self.window.LockOptPanel, False)
            syscontext.tempentity["CRAWLERUID"] = None
            
    def GetParentPath(self, strPath):  
        if not strPath:  
            return None;  
        lsPath = os.path.split(strPath);  
        if lsPath[1]:  
            return lsPath[0];  
        lsPath = os.path.split(lsPath[0]);  
        return lsPath[0];
    
        #获取脚本文件的当前路径
    def GetCurrentDir(self):
        #获取脚本路径
        path = sys.path[0]
        #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，
        #则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)
    
    def CopyResultDat2Csv(self, outputPath, filename, userLst):
        try:
            writer = csv.writer(file(os.path.join(outputPath, 
                                                  filename+".user.csv"),'a+b'))
            #add 'bd','qq','msn','email','at' after tag
            writer.writerow(['_id','sn','sx','vi','de','ad','un','an','fn','mn',
                             'ci','ei','iu','iv','tg','bd','qq','msn','email',
                             'at','fui'])
            
            for r in userLst:
                writer.writerow([r.get('_id'), 
                                 r.get(COLUMN_SCREENNAME), 
                                 r.get(COLUMN_SEX), 
                                 r.get(COLUMN_VERIFICATION_INFO), 
                                 r.get(COLUMN_DESCRIPTION), 
                                 r.get(COLUMN_ADDRESS), 
                                 r.get(COLUMN_USERNAME), 
                                 r.get(COLUMN_FOLLOWERS_NUM), 
                                 r.get(COLUMN_FRIENDS_NUM), 
                                 r.get(COLUMN_MSG_NUM), 
                                 r.get(COLUMN_WORK), 
                                 r.get(COLUMN_EDUCATION), 
                                 r.get(COLUMN_PROFILE_IMAGE_URL), 
                                 r.get(COLUMN_ISVIP), 
                                 r.get(COLUMN_USER_TAG),
                                 r.get(COLUMN_BIRTHDAY),
                                 r.get(COLUMN_QQ),
                                 r.get(COLUMN_MSN),
                                 r.get(COLUMN_EMAIL),
                                 r.get(COLUMN_CREATE_TIME), 
                                 r.get(COLUMN_USERERL_FOLLOWERS_IDS), 
                                 ])
        except Exception:
            s=sys.exc_info()
            msg = (u"write csv Error %s happened on line %d" % (s[1],
                                                                s[2].tb_lineno))
            logger.error(msg)
    
    def CopyMsgDat2Csv(self, outputPath, filename, msgLst):
        try:
            writer = csv.writer(file(os.path.join(outputPath, filename+
                                                  ".msg.csv"),'a+b'))
            writer.writerow(['消息ID','用户ID','用户名','屏幕名','用户头像','转发消息ID',\
                             '消息内容','消息URL','来源','图片URL','音频URL','视频URL',\
                             '转发数','评论数','发布时间','@用户'])
            for r in msgLst:
                writer.writerow([r.get(COLUMN_ID), 
                                 r.get(COLUMN_USERID), 
                                 r.get(COLUMN_USERNAME, ""), 
                                 r.get(COLUMN_SCRENNAME, ""), 
                                 r.get(COLUMN_USERIMG, ""), 
                                 r.get(COLUMN_RETWEETID, ""), 
                                 r.get(COLUMN_MSGCONTENT), 
                                 r.get(COLUMN_MSGURL), 
                                 r.get(COLUMN_SOURCENAME), 
                                 r.get(COLUMN_PICURL), 
                                 r.get(COLUMN_AUDIOURL), 
                                 r.get(COLUMN_VIDEOURL), 
                                 r.get(COLUMN_RETEETCOUNT), 
                                 r.get(COLUMN_COMMENTCOUNT), 
                                 r.get(COLUMN_PUBLISH_TIME), 
                                 r.get(COLUMN_NAMECARD), 
                                 ])
        except Exception:
            s=sys.exc_info()
            msg = (u"CopyMsgDat2Csv Error %s happened on line %d" % (s[1]
                                                                     ,s[2].tb_lineno))
            logger.error(msg)
            