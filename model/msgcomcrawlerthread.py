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
import wx
import workerpool
from Queue import Queue, Empty
import cPickle
import csv
import simplejson as json
from model.msgentity import * #@UnusedWildImport
from model.userentity import * #@UnusedWildImport
import os
from sina.weiborequest import getHtmlSource
import time
from model.msgcomcrawler import UsermsgCrawler
from model import syscontext

'''
SINA微博资料 标签：
更多显示项为空！
'''

from model.log4py import Log4py
logger = Log4py().getLogger('run')

class MsgComCrawlerThread(workerpool.Job):
    
    def __init__(self, result_queue, uid, task_info, threadID, window, threadNum, output_path, proxylist=[]):
        self.result_queue = result_queue
        self.uid = uid
        self.proxylist = proxylist
        self.gsid = task_info.get("gsid")[0]
        self.userinfo = {}
        self.msginfo = []
        #result：采集返回的数据
        #包含：用户信息和用户首页基本信息
        self.result = {}
        self.id = threadID
        self.window = window
        self.threadNum = threadNum
        self.output_path = output_path
        
    def run(self):
        while self.window.keepRunning :
            userid = self.uid
            try:
                now = time.time()
                nowTime = str(time.time()).replace(".", "")
                gsid = self.gsid
                userIndexUrl = "http://m.weibo.cn/home/homeData?hideAvanta=1&u=%s&page=1&&_=%s" % (userid, nowTime)
                userInfoUrl = "http://m.weibo.cn/setting/userInfoSetting?uid=%s&st=569d&" % (userid)
                self.userinfo['_id'] = userid.encode('utf-8')
                #user basic info page
                content = self.getHtmlSource(userIndexUrl, userid, gsid, "http://m.weibo.cn/u/%s?" % userid)
                if content == "":
                    msg = u"用户： %s 采集失败,case:返回用户信息为空！" % userid
                    logger.error(msg)
                    wx.CallAfter(self.window.WriteLog, msg)
                    break
                # print content.decode('gbk').encode('utf-8')
                if not self.getSinaWapUserWeiboInfo(content):
                    wx.CallAfter(self.window.WriteLog, u"===================")
                    msg = u"无效的用户ID：%s." % (userid)
                    wx.CallAfter(self.window.WriteLog, msg)
                    self.userinfo['fg'] = 4;
                    self.result["user"] = self.userinfo
                    self.result["msg"] = self.msginfo
                    self.result_queue.put(self.result)
                    break
                #user detail info page
                content = self.getHtmlSource(userInfoUrl, userid, gsid, "http://m.weibo.cn/users/%s?" % userid)
                # infoStatus = self.getSinaWapUserInfo(content)
                
                self.window.totalCount += 2
                self.window.curCount += 2
                
                allfuid = ''
                self.userinfo[COLUMN_USERERL_FOLLOWERS_IDS] = allfuid.encode('utf-8')
                self.result["user"] = self.userinfo
                
                t = time.strftime( '%Y-%m-%d-%H-%M-%S', time.localtime( time.time() ))
                self.msginfo.sort(key=lambda obj:obj.get('pt'))
                #按采集的人写消息文件
                
                CopyMsgDat2Csv(self.output_path, t+"-"+str(self.userinfo.get("_id", "").decode("utf8")), self.msginfo)
                
                elapsed = time.time() - now
                msg = u'耗时 : %ds 采集用户：%s , 微博数(原创+转发): %d' % (int(elapsed), self.userinfo[COLUMN_SCREENNAME], len(self.msginfo))
                logger.info(msg)
                wx.CallAfter(self.window.WriteLog, msg)
                
                self.result["msg"] = self.msginfo
                self.result_queue.put(self.result)
                #self.window.finishedCount += 1
            except Exception:
                self.userinfo['fg'] = 13;
                self.result["user"] = self.userinfo
                self.result["msg"] = self.msginfo
                self.result_queue.put(self.result)
                s=sys.exc_info()
                msg = (u"getSinaWapUserInfo Error %s happened on line %d" % (s[1],s[2].tb_lineno))
                logger.error(msg)
            finally:
                #wx.CallAfter(self.window.UpdateCrawlProcess, self.window.finishedCount)
                break
        
    def getSinaWapUserWeiboInfo(self, html):
        try:
            # import chardet
            # print chardet.detect(html)
            html = html.decode('unicode-escape').encode('utf-8')
            # print html
            # print chardet.detect(html)
            if '用户不存在哦!' in html:
                #logger.error('getSinaWapUserWeiboInfo用户不存在哦!')
                return False
            '''
            parse for m.weibo.cn
            '''
            # open('prettydad.html','w').write(html)
            userinfoObj = None
            try:
                userinfoObj = json.loads(html)
            except:
                html = html.replace('\n', '')
                html = html.replace('\r', '')
                html = html.replace('"', '\\"')
                html = html.replace(':\\"', ':"')
                html = html.replace('\\":', '":')
                html = html.replace(',\\"', ',"')
                html = html.replace('\\",', '",')
                html = html.replace('{\\"', '{"')
                html = html.replace('\\"}', '"}')
                html = html.replace('[\\"', '["')
                html = html.replace('\\"]', '"]')
                html = html.replace('\\(', '\\\\(')
                userinfoObj = json.loads(html)
            #user base info
            user = userinfoObj.get("userInfo", None)
            if user:
                #user name
                weibohao = user.get("weihao","")
                if weibohao == 0:
                    weibohao = user.get("id","")
                self.userinfo[COLUMN_USERNAME] = weibohao
                #screen name
                self.userinfo[COLUMN_SCREENNAME] = user.get("name","").encode('utf-8')
                #profile_image_url
                self.userinfo[COLUMN_PROFILE_IMAGE_URL] = user.get("profile_image_url","").encode('utf-8')
                #description
                self.userinfo[COLUMN_DESCRIPTION] = user.get("description","").encode('utf-8')
                #mblogNum
                self.userinfo[COLUMN_MSG_NUM] = user.get("mblogNum",0)
                #attNum
                self.userinfo[COLUMN_FOLLOWERS_NUM] = user.get("attNum",0)
                #fansNum
                self.userinfo[COLUMN_FRIENDS_NUM] = user.get("fansNum",0)
                #ta
                userSex = user.get("ta","").encode('utf-8')
                if userSex == "他":
                    sex = "男"
                elif userSex == "她" :
                    sex = "女"
                else:
                    sex = "ta"
                self.userinfo[COLUMN_SEX] = sex
                #nativePlace
                self.userinfo[COLUMN_ADDRESS] = user.get("nativePlace","").encode('utf-8')
                #vip
                vipFlag = user.get("vip")
                if vipFlag and vipFlag!=0 and len(vipFlag) > 0:
                    vipFlag = vipFlag[0]
                vip = 0
                popman = 0
                vipFlag = str(vipFlag)
                if "5338.gif" in vipFlag:
                    vip = 1
                elif "5547.gif" in vipFlag:
                    popman = 1
                else:
                    pass
                self.userinfo[COLUMN_ISDAREN] = popman
                self.userinfo[COLUMN_ISVIP] = vip
                
                wx.CallAfter(self.window.WriteLog, u"===================")
                msg = u"正在采集用户： %s,微博数：%s \t" % (self.userinfo[COLUMN_SCREENNAME], self.userinfo[COLUMN_MSG_NUM])
                wx.CallAfter(self.window.WriteLog, msg)
                
                #获取用户微博页数
                maxPage = int((int(self.userinfo[COLUMN_MSG_NUM])-1)/44)+1
                if maxPage >= 1:
                    wx.CallAfter(self.window.SetCrawlProcessRange, (maxPage*1+self.window.processRangeVal))
                    msg_list = self.getUserOtherMsgInfo(maxPage)
                    self.window.totalCount += (maxPage)
                    self.msginfo.extend(msg_list)
            else:
                #logger.error('sina data maybe changed format!')
                return False
               
        except Exception:
            s=sys.exc_info()
            msg = (u"getSinaWapUserInfo Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
            return False
        return True
    
    def getSinaWapUserInfo(self, html):
        try:
            html = html.encode('utf-8')
            if '用户不存在哦!' in html:
                #logger.error('getSinaWapUserWeiboInfo用户不存在哦!')
                return 'user is empty'
            #user detail info
            userinfoObj = json.loads(html)
            userDetailInfo = userinfoObj.get("userInfoDetail", None)
            if userDetailInfo:
                if userDetailInfo.get("ok", 0) == 1:
                    #basicInfo
                    detailInfoObj = userDetailInfo.get("basicInfo", None)
                    if detailInfoObj:
                        #created_at
                        self.userinfo[COLUMN_CREATE_TIME] = detailInfoObj.get("created_at", "").encode('utf-8')
                        #birthday
                        self.userinfo[COLUMN_BIRTHDAY] = detailInfoObj.get("birthday", "")
                        #verified
                        #verified_reason
                        self.userinfo[COLUMN_VERIFICATION_INFO] = detailInfoObj.get("verified_reason", "").encode('utf-8')
                        #user contact info
                        #qq
                        self.userinfo[COLUMN_QQ] = detailInfoObj.get("qq", "").encode('utf-8')
                        #email
                        self.userinfo[COLUMN_EMAIL] = detailInfoObj.get("email", "").encode('utf-8')
                        #msn
                        self.userinfo[COLUMN_MSN] = detailInfoObj.get("msn", "").encode('utf-8') 
                    #editInfo
                    infoObjs = userDetailInfo.get("editInfo", None)
                    editInfo = ""
                    if infoObjs:
                        for info in infoObjs:
                            editInfo += info.get("school")+","
                    editInfo = editInfo[:editInfo.rfind(',')]
                    #careerInfo
                    infoObjs = userDetailInfo.get("careerInfo", None)
                    careerInfo = ""
                    if infoObjs:
                        for info in infoObjs:
                            careerInfo += info.get("company")+","
                    careerInfo = careerInfo[:careerInfo.rfind(',')]
                    self.userinfo[COLUMN_EDUCATION] = editInfo.encode('utf-8')
                    self.userinfo[COLUMN_WORK] = careerInfo.encode('utf-8')
                else:
                    return 'user detail load failure'
            #user tags
            #tags
            userTagsObj = userinfoObj.get("tags", None)
            userTagStr = ""
            if userTagsObj:
                if userTagsObj.get("ok", 0) == 1:
                    #usertags
                    tags = (userTagsObj.get("usertags"))
                    for tag in tags:
                        userTagStr += tag.get("name", "")+","
                    userTagStr = userTagStr[:userTagStr.rfind(',')]
                    self.userinfo[COLUMN_USER_TAG] = userTagStr
                else:
                    return 'user tag load failure'
        except Exception:
            s=sys.exc_info()
            msg = (u"getSinaWapUserInfo Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
            return "exception"
        return 'success'
    
    def getUserOtherMsgInfo(self, maxPage):
        q = Queue(0)
        msg = UsermsgCrawler(result_queue=q, thread_id=1, window=self.window, thread_num=self.threadNum, 
                                 output_path=self.output_path, user=self.userinfo, max_page=maxPage, sina=syscontext.LOGIN_SINA_COM)
        msg.run()
        msg_list = []
        try:
            for i in range(q.qsize()): #@UnusedVariable
                msg_list.extend(q.get(block=False))
        except Empty:
            pass # Success
        return msg_list
    
    def getProxyIP(self):
        if len(self.proxylist)>=1:
            ip = self.proxylist[0]
            self.proxylist.remove(ip)
            self.proxylist.append(ip)
        else:
            return ""
        return ip
    
    def getHtmlSource(self, url, userid, gsid, refUrl):
        content = ""
        for i in range(3): #@UnusedVariable
            proxyip = self.getProxyIP()
            try:
                if not url.startswith("http://"):
                    url = "http://"+url
                headers = {'Host': 'm.weibo.cn',
                           'User-Agent': 'android',
                           'Accept': '*/*',
                           'Connection': 'keep-alive',
                           'Accept-encoding': 'gzip, deflate',
                           'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                           'X-Requested-With': 'XMLHttpRequest',
                           }
                if refUrl:
                    headers['Referer'] = refUrl
                headers['Cookie'] = 'gsid_CTandWM=' + gsid + '; _WEIBO_UID='+userid
                content = getHtmlSource(url, headers=headers, proxyip=proxyip)
                if "登录" in content and "密码" in content and "注册" in content :
                    content = ""
                elif "微博精选" in content and "热门转发" in content:
                    content = ""
                elif "抱歉，你的帐号存在异常，暂时无法访问" in content and "解除访问限制" in content:
                    content = ""
                #time.sleep(0.2*random.randint(1, 10))
            except Exception:
                s=sys.exc_info()
                msg = (u"get html Error %s happened on line %d" % (s[1],s[2].tb_lineno))
                logger.error(msg)
                content = ""
            if content != "":
                break
        return content
    
def CopyResultDat2Csv(outputPath, filename):
        try:
            writer = csv.writer(file(outputPath +'/'+ filename + '.csv','a+b'))
            writer.writerow(['_id','sn','sx','vi','de','ad','un','an','fn','mn','ci','ei','iu','iv','tg','bd','qq','msn','email','at','fui'])
            
            EOF = False
            f = open(outputPath +'/'+ filename, "r+b")
            while not EOF:
                try:
                    result = cPickle.load(f)
                except(EOFError):
                    EOF = True
                else:
                    for r in result:
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
            msg = (u" Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)

def CopyMsgDat2Csv(outputPath, filename, msgLst):
        try:
            writer = csv.writer(file(os.path.join(outputPath, filename+".msg.csv"),'a+b'))
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
            msg = (u"CopyMsgDat2Csv Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)