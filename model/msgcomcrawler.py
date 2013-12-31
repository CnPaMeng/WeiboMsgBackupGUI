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

from __future__ import division

import sys
from lxml.html.soupparser import fromstring
from lxml.html import tostring
import re
import time
import json
import random
import workerpool
from Queue import Queue, Empty

import wx

from model.msgentity import * #@UnusedWildImport
from sina.weiborequest import getMillitime
from sina.sinaWburl2ID import midToStr, sinaWburl2ID

from model.log4py import Log4py
logger = Log4py().getLogger('run')

#用户消息采集类
#解析用首页，调用采集工作累，创建采集线程
#限于.COM
class UsermsgCrawler(workerpool.Job):
    
    def __init__(self, **kwargs):
        #print kwargs
        self.result_queue = kwargs.get("result_queue", "")
        self.thread_id = kwargs.get("thread_id", "")
        self.window = kwargs.get("window", "")
        self.thread_num = kwargs.get("thread_num", "")
        self.output_path = kwargs.get("output_path", "")
        self.user = kwargs.get("user", {})
        self.max_page = kwargs.get("max_page", 1)
        self.sina = kwargs.get("sina", 1)
        #用户消息列表
        self.msgLst = []
        self.xpathconfig = XpathConfig()
        self.xpathType = ""
        
    def run(self):
        try:
            self.parsePagelist(self.max_page)
        except:
            s=sys.exc_info()
            msg = (u"thread Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
        finally:
            self.result_queue.put(self.msgLst)
        
    #解析更多页
    #需要先抽取用户首页最新微博id作为end_id
    def parsePagelist(self, maxPage):
        url = ""
        userid = self.user.get("_id", "")
        max_id = ""
        end_id = ""
        html = ""
        msg = u"正在采集用户:%s 第  %s 页 / 共 %s 页 微博." % (self.user.get("sn"), 1, maxPage)
        #print msg
        wx.CallAfter(self.window.WriteLog, msg)
        try:
            eachpageCount = 0
            hasMore = 1
            #抽取第一页微博
            #每页循环lazy load MAX:[0,1,2]3次
            while hasMore and eachpageCount <= 2:
                rnd = getMillitime()
                k_rnd = random.randint(10, 60)
                page = 1
                if eachpageCount == 0:
                    url = "http://weibo.com/aj/mblog/mbloglist?_wv=5&page=%s&count=50&pre_page=%s&end_id=%s&_k=%s&_t=0&end_msign=-1&uid=%s&__rnd=%s" % (page, (page-1), end_id, rnd+str(k_rnd), userid, rnd)
                else:
                    #url 中 _k 为 时间戳（毫秒计）
                    url = "http://weibo.com/aj/mblog/mbloglist?_wv=5&page=%s&count=15&pre_page=%s&end_id=%s&_k=%s&_t=0&max_id=%s&pagebar=%s&uid=%s&__rnd=%s" % (page, (page), end_id, rnd+str(k_rnd+1), max_id, eachpageCount-1, userid,  getMillitime())
                if not html:
                    html = self.getAjaxmsg(url, "http://weibo.com/u/%s" % userid)
                    html = self.getHtmlFromJson(html)
                hasMore,feedmsgLst,max_id = self.parseFeedlist(html)
                if eachpageCount == 0:
                    end_id = feedmsgLst[0].get("mid", "0")
                #存入消息列表返回
                self.msgLst.extend(feedmsgLst)
                eachpageCount += 1
                html = ""
            
            self.window.totalCount += maxPage*3
            wx.CallAfter(self.window.SetCrawlProcessRange, (maxPage*1+self.window.processRangeVal))
            pool = workerpool.WorkerPool( self.thread_num )
            q = Queue(0)
            for i in range(2, maxPage+1):
                try:
                    #开启翻页采集线程
                    job = UsermsgJob(result_queue=q,thread_id=i,user=self.user,end_id=end_id,
                                     max_page=maxPage, msg_crawler=self,window=self.window)
                    pool.put(job)
                except:
                    s=sys.exc_info()
                    msg = (u"jobThread ERROR %s happened on line %d" % (s[1],s[2].tb_lineno))
                    logger.error(msg)
            pool.shutdown()
            pool.wait()
            try:
                for i in range(q.qsize()):
                    self.msgLst.extend(q.get(block=False))
            except Empty:
                pass # Success
        except:
            s=sys.exc_info()
            msg = (u"parsePagelist Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
    
    #解析用户消息列表
    def parseFeedlist(self, html):
        feedDoc = fromstring(html)
        self.config = self.xpathconfig.getIndexConfig('v1')
        nodeLst = feedDoc.xpath(self.config.get("USER_FEEDLIST_XPATH"))
        moreNode = feedDoc.xpath(self.config.get("MORE_FEEDLIST_XPATH"))
        feedmsgLst = []
        hasMore = 0
        max_id = ""
        for node in nodeLst:
            try:
                msg,rtmsg = self.parseFeed(node)
                if msg:
                    max_id = msg.get("mid")
                    feedmsgLst.append(msg)
                if rtmsg:
                    feedmsgLst.append(rtmsg)
            except:
                #s=sys.exc_info()
                #msg = (u"parseFeedlist Error %s happened on line %d" % (s[1],s[2].tb_lineno))
                #logger.error(msg)
                continue
        if moreNode:
            #需要解析更多
            hasMore = 1
        return hasMore,feedmsgLst,max_id
    
    def getHtmlFromJson(self, html):     
        return json.loads(html).get("data")
    
    #解析消息
    def parseFeed(self, node):
        rtmsg = {}
        msg = {}
        try:
            #消息id
            mid = node.get("mid", "")
            if mid:
                try:
                    node = fromstring(tostring(node).decode('unicode-escape'))
                except:
                    node = fromstring(tostring(node))
                msg = self.parseCommon(node, "msg")
                if msg:
                    #转发微博
                    rtmsgNode = node.xpath(self.config.get("MSG_RETWEET_XPATH"))
                    if rtmsgNode:
                        try:
                            rtmsg = self.parseRefeed(rtmsgNode[0])
                            msg[COLUMN_RETWEETID] = rtmsg.get("mid", "")
                        except:
                            #s=sys.exc_info()
                            #msg = (u"rtmsgNode Error %s happened on line %d" % (s[1],s[2].tb_lineno))
                            #logger.error(msg)
                            pass
                    msg[COLUMN_ID] = mid
                    msg[COLUMN_MSGURL] = midToStr(mid)
                    msg[COLUMN_USERNAME] = self.user.get("un", "")
                    msg[COLUMN_USERID] = self.user.get("ui", "")
                    msg[COLUMN_SCRENNAME] = self.user.get("sn", "")
                    msg[COLUMN_USERIMG] = self.user.get("iu", "")
                    # print '解析微博成功：', msg[COLUMN_MSGCONTENT]
        except:
            s=sys.exc_info()
            errmsg = (u"rtmsgNode Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(errmsg)
            msg = {}
        #self.msgLst.append(msg)
        return msg,rtmsg
    
    #解析转发消息
    def parseRefeed(self, node):
        node = fromstring(tostring(node))
        #ui
        userNode = node.xpath(self.config.get("RT_USER_XPATH"))
        if userNode:
            userNode = userNode[0]
            ui = userNode.get("usercard", "").replace("id=", "")
            sn = userNode.get("nick-name", " ")
            un = userNode.get("href", "").replace("/", "")
        else:
            return {}
        rtmsg = self.parseCommon(node, "rtmsg")
        if rtmsg:
            rtmsg[COLUMN_USERID] = ui
            rtmsg[COLUMN_USERNAME] = un
            rtmsg[COLUMN_SCRENNAME] = sn
            #转发消息URL
            muNode = node.xpath("//div/div/div/div[@class='WB_from']/a[@title]")
            mu = ""
            mid = ""
            if muNode:
                mu = muNode[0].get("href", "").split("/")[-1]
                mid = sinaWburl2ID(mu)
            rtmsg[COLUMN_ID] = mid
            rtmsg[COLUMN_MSGURL] = mu
        return rtmsg
        
    def parseCommon(self, node , type="msg"): #@ReservedAssignment
        try:
            config = self.xpathconfig.getMsgConfig_V1(type)
            #发布时间
            ptNode = node.xpath(config.get("MSG_TIME_XPATH"))
            pt = ""
            if ptNode:
                pt = ptNode[0].get("title")
                pt = self.parsePubtime(pt)
            else:
                return {}
            #消息文本
            mt = node.xpath(config.get("MSG_TEXT_XPATH"))[0].text_content()
            #@提及用户
            nc = []
            for ncNode in node.xpath(config.get("MSG_NAMECARD_XPATH")):
                nc.append(ncNode.text_content())
            nc = ",".join(nc)
            #来自
            srn = "新浪微博"
            srnNode = node.xpath(config.get("MSG_FROM_XPATH"))
            if srnNode:
                srn = srnNode[0].text_content()
            #评论 转发
            fromStr = node.xpath(config.get("MSG_BASE_XPATH"))[0].text_content()
            rc = 0
            cc = 0
            rcNode = re.findall("转发\((.\d*)\)", str(fromStr))
            if rcNode:
                rc = int(rcNode[0])
            rcNode = re.findall("评论\((.\d*)\)", str(fromStr))
            if rcNode:
                cc = int(rcNode[0])
            #图片和视频/音频
            mediaNode = node.xpath(config.get("MSG_PIC_XPATH"))
            pu = ""
            if mediaNode:
                pu = mediaNode[0].get("src")
            mediaNode = node.xpath(config.get("MSG_VIDEO_XPATH"))
            vu = ""
            if mediaNode:
                vu = mediaNode[0].get("action-data")
            return self.initMsg(mt=mt, nc=nc, srn=srn, pt=pt, rc=rc, cc=cc, pu=pu, vu=vu)
        except Exception:
            s=sys.exc_info()
            msg = (u"parseCommon Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
            return {}
    
    def initMsg(self, **kwargs):
        try:
            msg = {}
            msg[COLUMN_ID] = kwargs.get("mid", "")
            msg[COLUMN_USERNAME] = kwargs.get("un", "").strip().encode("utf-8")
            msg[COLUMN_USERID] = kwargs.get("ui", "")
            msg[COLUMN_SCRENNAME] = kwargs.get("sn", "").strip().encode("utf-8")
            msg[COLUMN_USERIMG] = kwargs.get("iu", "")
            msg[COLUMN_MSGCONTENT] = kwargs.get("mt", "").encode("utf-8")
            msg[COLUMN_MSGURL] = kwargs.get("mu", "")
            msg[COLUMN_SOURCENAME] = kwargs.get("srn", "").strip().encode("utf-8")
            msg[COLUMN_PICURL] = kwargs.get("pu", "")
            msg[COLUMN_AUDIOURL] = kwargs.get("au", "")
            msg[COLUMN_VIDEOURL] = kwargs.get("vu", "")
            msg[COLUMN_RETEETCOUNT] = kwargs.get("rc", "")
            msg[COLUMN_COMMENTCOUNT] = kwargs.get("cc", "")
            msg[COLUMN_PUBLISH_TIME] = kwargs.get("pt", "")
            msg[COLUMN_NAMECARD] = kwargs.get("nc", "").strip().encode("utf-8")
            msg[COLUMN_RETWEETID] = kwargs.get("ri", "")
        except Exception:
            s=sys.exc_info()
            msg = (u"initMsg Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
        return msg
    
    #转换时间为UNIX时间戳
    def parsePubtime(self, ptStr):
        try:
            pt = int(time.mktime(time.strptime(ptStr,'%Y-%m-%d %H:%M')))
        except:
            pt = int(time.time())
        return pt
    
    #获取用户首页HTML
    def getUserIndex(self, url):
        headers = {"Host":"weibo.com",
                   "User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1",
                   "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
                   "Accept-Encoding":"gzip, deflate",
                   "Connection":"keep-alive",
                   }
        for i in range(3): #@UnusedVariable
            try:
                self.window.curCount += 1
                html = self.sina.get_content_head(url, headers=headers)
            except:
                continue
            if html:
                break
        return html
    
    #获取AJAX加载消息HTML
    def getAjaxmsg(self, url, refUrl):
        headers = {"Host":"weibo.com",
                   "User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1",
                   "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
                   "Accept-Encoding":"gzip, deflate",
                   "Connection":"keep-alive",
                   "Content-Type":"application/x-www-form-urlencoded",
                   "X-Requested-With":"XMLHttpRequest",
                   "Referer":refUrl,
                   }
        for i in range(3): #@UnusedVariable
            try:
                #print url
                self.window.curCount += 1
                html = self.sina.get_content_head(url, headers=headers)
            except:
                continue
            if html:
                break
        return html
        
    def getPanelInfo(self, doc, strXPath):
        try:
            npos = doc.text_content().find(strXPath)
            if npos == -1:
                return ""
            strContent = doc.text_content()[npos:-1]
            npos = strContent.find("})")
            if npos == -1:
                return ""
            strContent = strContent[0:npos+1]
            strContent = (strContent[strContent.find("\"html\":\"")+8:-4])
            if "v2" in self.xpathType:
                strContent = strContent.decode('unicode-escape')
            strContent = re.sub(r"(\\n)*(\\t)*(\\ /)*(\\)*", "", strContent)
            strContent = re.sub(r"\\/", "/", strContent)
            if strContent:
                strContent = strContent.replace("&lt;", "<").replace("&gt;", ">").replace("nbsp;", "")
            else:
                return ""
        except Exception:
            s=sys.exc_info()
            msg = (u"getPanelInfo Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
            return ""
        return strContent

#用户消息采集job
#从第二页开始线程采集
class UsermsgJob(workerpool.Job):
    
    def __init__(self, **kwargs):
        #print kwargs
        self.result_queue = kwargs.get("result_queue", "")
        #thread id同时作为页数
        self.thread_id = kwargs.get("thread_id", "")
        self.user = kwargs.get("user", "")
        self.end_id = kwargs.get("end_id", "")
        self.msgcrawler = kwargs.get("msg_crawler", "")
        self.window = kwargs.get("window", "")
        self.max_page = kwargs.get("max_page", 1)
        #用户消息列表
        self.msgLst = []
        
    def run(self):
        while self.window.keepRunning :
            page = self.thread_id
            msg = u"正在采集用户:%s 第  %s 页 / 共 %s 页 微博." % (self.user.get("sn"), page, self.max_page)
            #print msg
            wx.CallAfter(self.window.WriteLog, msg)
            try:
                html = ""
                userid = self.user.get("_id")
                
                end_id = self.end_id
                eachpageCount = 0
                hasMore = 1
                max_id = ""
                crawler = self.msgcrawler
                #每页循环lazy load MAX:[0,1,2]3次
                while hasMore and eachpageCount <= 2:
                    rnd = getMillitime()
                    k_rnd = random.randint(10, 60)
                    if eachpageCount == 0:
                        url = "http://weibo.com/aj/mblog/mbloglist?_wv=5&page=%s&count=50&pre_page=%s&end_id=%s&_k=%s&_t=0&end_msign=-1&uid=%s&__rnd=%s" % (page, (page-1), end_id, rnd+str(k_rnd), userid, rnd)
                    else:
                        #url 中 _k 为 时间戳（毫米计）
                        url = "http://weibo.com/aj/mblog/mbloglist?_wv=5&page=%s&count=15&pre_page=%s&end_id=%s&_k=%s&_t=0&max_id=%s&pagebar=%s&uid=%s&__rnd=%s" % (page, (page), end_id, rnd+str(k_rnd+1), max_id, eachpageCount-1, userid,  getMillitime())
                    html = crawler.getAjaxmsg(url, "http://weibo.com/u/%s" % userid)
                    html = crawler.getHtmlFromJson(html)
                    hasMore,feedmsgLst,max_id = crawler.parseFeedlist(html)
                    #存入消息列表返回
                    self.msgLst.extend(feedmsgLst)
                    eachpageCount += 1
                self.result_queue.put(self.msgLst)
                self.window.finishedCount += 1
            except:
                s=sys.exc_info()
                msg = (u"parsePagelist Error %s happened on line %d" % (s[1],s[2].tb_lineno))
                logger.error(msg)
            finally:
                wx.CallAfter(self.window.UpdateCrawlProcess, self.window.finishedCount)
                break
 
#Created on 2012-8-31
#消息XPATH配置
#@author: Zoe
class XpathConfig():
    
    def __init__(self):
        pass
    
    def getMsgConfig_V1(self, _type="msg"):
        #用户消息xpath配置
        __usermsgXpath = {"MSG_TEXT_XPATH":"//div[@class='WB_detail']/div[@class='WB_text']",
                        "MSG_NAMECARD_XPATH":"//div[@class='WB_detail']/div[@class='WB_text']/a[@usercard]",
                        "MSG_TIME_XPATH":"//div[@class='WB_detail']/div[@class='WB_func clearfix']/div[@class='WB_from']/a[@date]",
                        "MSG_FROM_XPATH":"//div[@class='WB_detail']/div[@class='WB_func clearfix']/div[@class='WB_from']/a[@target and not(@date)]",
                        "MSG_BASE_XPATH":"//div[@class='WB_detail']/div[@class='WB_func clearfix']/div[@class='WB_handle']",
                        "MSG_PIC_XPATH":"//div[@class='WB_detail']/ul/li[not(@action-type)]/div/img",
                        "MSG_VIDEO_XPATH":"//div[@class='WB_detail']/ul/li[@action-type]",
                        }
        #用户转发消息xpath配置
        __userrtmsgXpath = {"MSG_TEXT_XPATH":"//div/div[@class='WB_text']",
                          "MSG_NAMECARD_XPATH":"//div/div[@class='WB_text']/a[@usercard]",
                          "MSG_TIME_XPATH":"//div/div/div/div[@class='WB_from']/a[@date]",
                          "MSG_FROM_XPATH":"//div/div/div/div[@class='WB_from']/a[@target and not(@date)]",
                          "MSG_BASE_XPATH":"//div/div/div/div[@class='WB_handle']",
                          "MSG_PIC_XPATH":"//div/ul/li[not(@action-type)]/div/img",
                          "MSG_VIDEO_XPATH":"//div/ul/li[@action-type]",
                        }
        
        #供调用配置
        msgxpath = {"msg":__usermsgXpath, "rtmsg":__userrtmsgXpath}
        return msgxpath.get(_type, "")
    
    def getMsgConfig_V2(self, _type="msg"):
        #用户消息xpath配置
        __usermsgXpath = {"MSG_TEXT_XPATH":"//dl/dd[@class]/p[@node-type]",
                        "MSG_NAMECARD_XPATH":"//dl/dd/p[@node-type]/a[@usercard]",
                        "MSG_TIME_XPATH":"//dl/dd/p/a[@class='date']",
                        "MSG_FROM_XPATH":"//dl/dd/p/a[(@target) and not(@action-type)]",
                        "MSG_BASE_XPATH":"//dl/dd/p/span",
                        "MSG_PIC_XPATH":"//div[@class='WB_detail']/ul/li[not(@action-type)]/div/img",
                        "MSG_VIDEO_XPATH":"//div[@class='WB_detail']/ul/li[@action-type]",
                        }
        #用户转发消息xpath配置
        __userrtmsgXpath = {"MSG_TEXT_XPATH":"//div/div[@class='WB_text']",
                          "MSG_NAMECARD_XPATH":"//div/div[@class='WB_text']/a[@usercard]",
                          "MSG_TIME_XPATH":"//div/div/div/div[@class='WB_from']/a[@title]",
                          "MSG_FROM_XPATH":"//div/div/div/div[@class='WB_from']/a[@target]",
                          "MSG_BASE_XPATH":"//div/div/div/div[@class='WB_handle']",
                          "MSG_PIC_XPATH":"//div/ul/li[not(@action-type)]/div/img",
                          "MSG_VIDEO_XPATH":"//div/ul/li[@action-type]",
                        }
        
        #供调用配置
        msgxpath = {"msg":__usermsgXpath, "rtmsg":__userrtmsgXpath}
        return msgxpath.get(_type, "")
    
    def getIndexConfig(self, name="v1"):
        __newindexXpath = {"USER_PROFILE_BLOCK" : "{\"pid\":\"pl_profile_photo\"",
                           "MSG_COUNT_XPATH" : "//ul/li[3]/a/strong",
                           "USER_IMG_XPATH" : "//div/img",
                           "MSG_COUNT_XPATH_BV" : "//ul/li[3]/div/a[@id]",
                           "USER_IMG_XPATH_BV" : "//div[@id='profileHead']/div/div/a/img",
                           "USER_HISINFO_BLOCK" : "{\"pid\":\"pl_profile_hisInfo\"",
                           "USER_SCREENNAME_XPATH" : "//div/span[@class='name']",
                           "USER_USERNAME_XPATH" : "//div/div/div/a[@class]",
                           "USER_USERNAME_XPATH_BV" : "//div[@class='other_info']/p/a",
                           "USER_FEEDLIST_BLOCK" : "{\"pid\":\"pl_content_hisFeed\"",
                           "USER_FEEDLIST_XPATH" : "//div[(@mid) and (@action-type)]",
                           "MORE_FEEDLIST_XPATH" : "//div[@class='W_loading']",
                           "MSG_RETWEET_XPATH" : "//div[@class='WB_detail']/div[@node-type='feed_list_forwardContent']",
                           "RT_USER_XPATH" : "//div/div[@class='WB_info']/a[@usercard]",
                           }
        __trialindexXpath = {"USER_PROFILE_BLOCK" : "{\"pid\":\"pl_content_litePersonInfo\"",
                           "MSG_COUNT_XPATH" : "//ul/li[3]/a/strong",
                           "USER_IMG_XPATH" : "//div/div/div/a[@class='face']/img",
                           "MSG_COUNT_XPATH_BV" : "//div[@id='profileHead']/div/div/a/img",
                           "USER_IMG_XPATH_BV" : "//div[@id='profileHead']/div/div/a/img",
                           "USER_HISINFO_BLOCK" : "{\"pid\":\"pl_content_hisPersonalInfo\"",
                           "USER_SCREENNAME_XPATH" : "//div/span[@class='name']",
                           "USER_USERNAME_XPATH" : "//div[@class='perAll_info']/p/a[@class]",
                           "USER_USERNAME_XPATH_BV" : "//div[@class='other_info']/p/a",
                           "USER_FEEDLIST_BLOCK" : "{\"pid\":\"pl_content_hisFeed\"",
                           "USER_FEEDLIST_XPATH" : "//div[(@mid) and (@action-type)]",
                           #"USER_FEEDLIST_XPATH" : "//dl[(@mid) and (@action-type)]",
                           "MORE_FEEDLIST_XPATH" : "//div[@class='W_loading']",
                           #"MSG_RETWEET_XPATH" : "//dl/dt[@node-type='feed_list_forwardContent']",
                           "MSG_RETWEET_XPATH" : "//div[@class='WB_detail']/div[@node-type='feed_list_forwardContent']",
                           #"RT_USER_XPATH" : "//dl/dt/a[@usercard]",
                           "RT_USER_XPATH" : "//div/div[@class='WB_info']/a[@usercard]",
                           }
        
        
        xpathConfig = {"v1": __newindexXpath, "v2": __trialindexXpath}
        return xpathConfig.get(name, "")
