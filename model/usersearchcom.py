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
import json
import threading
import wx

from model.log4py import Log4py
from model import syscontext
from lxml.html.soupparser import fromstring
from lxml.html import tostring

logger = Log4py().getLogger('run')

class UserSearchThread(threading.Thread):
    
    def __init__(self, searchName, window):
        threading.Thread.__init__(self)
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        self.result = {}
        self.searchName = searchName
        self.window = window
        self.sina = syscontext.LOGIN_SINA_COM
        
    def run(self):
        try:
            wx.CallAfter(self.window.EnableMainWin, False)
            searchResult = ""
            url = "http://s.weibo.com/user/%s&Refer=SUer_box" % (self.searchName)
            #user search info page
            headers = {'Host':'s.weibo.com',
                       'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1',
                       'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Language':'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                       'Accept-Encoding':'gzip, deflate',
                       'Connection':'keep-alive',
                       'Referer':'http://s.weibo.com',
                       }
            content = self.sina.get_content_head(url, headers)
            if content == "":
                msg = u"%s failure:获取网页内容为空！" % self.id
                logger.error(msg)
                searchResult = 'error'
            if not self.getUserInfo(content):
                self.result['fg'] = 4;
                searchResult = 'failure'
            else:
                searchResult = json.dumps(self.result).decode('unicode_escape') 
            #self.window.finishedCount += 1
        except Exception:
            self.result['fg'] = 13;
            searchResult = 'error'
            s=sys.exc_info()
            msg = (u"getSinaUserInfo Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
        finally:
            wx.CallAfter(self.window.EnableMainWin, True)
            wx.CallAfter(self.window.ShowSearchRes, searchResult)
            
    '''
    #解析用户
    '''
    def getUserInfo(self, html):
        try:
            if '搜索结果为空' in html:
                #print (u'weibo用户不存在!')
                return False
            if '您当前访问的用户状态异常' in html:
                #print (u'weibo用户状态异常!')
                return False
            html = self.getPanelInfo(html, '{\"pid\":\"pl_user_feedList\"')
            root = fromstring(html)
            user_divs = root.xpath("//div[@class='list_person clearfix']")
            if len(user_divs) > 0:
                users = []
                for div in user_divs:
                    user = {}
                    div = tostring(div , encoding='utf-8')
                    div = fromstring(div)
                    try:
                        iu_node = div.xpath("//div[@class='person_pic']/a/img")[0]
                        user['iu'] = iu_node.get("src")
                        user['sn'] = div.xpath("//div[@class='person_detail']/p[@class='person_name']")[0].text_content()
                        user['uid'] = iu_node.get("uid")
                        
                        sx_node = div.xpath("//div[@class='person_detail']/p[@class='person_addr']/span[@class='male m_icon']")
                        sx = ''
                        if sx_node:
                            sx = sx_node[0].get('title')
                        user['sx'] = sx
                        ad_node = div.xpath("//div[@class='person_detail']/p[@class='person_addr']")
                        ad = ''
                        if ad_node:
                            ad = ad_node[0].text_content()
                        user['ad'] = ad
                        num_node = div.xpath("//div[@class='person_detail']/p[@class='person_num']")
                        num = ''
                        if num_node:
                            num = num_node[0].text_content()
                        user['num'] = num
                        de_node = div.xpath("//div[@class='person_detail']/div[@class='person_info']")
                        de = ''
                        if de_node:
                            de = de_node[0].text_content()
                        user['de'] = de
                        users.append(user)
                    except:
                        pass
                self.result['users'] = users
            else:
                return False
        except Exception:
            s=sys.exc_info()
            msg = (u"getUserMsgInfo Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
            return False
        return True
    
    def getPanelInfo(self, html, strXPath):
        try:
            npos = html.find(strXPath)
            if npos == -1:
                return ""
            strContent = html[npos:-1]
            npos = strContent.find("})</script>")
            if npos == -1:
                return ""
            strContent = strContent[0:npos+len('})</script>')]
            strContent = strContent[strContent.find("\"html\":\"")+8: -1-(len('})</script>'))]
            strContent = strContent.replace(r"\ /", "")
            strContent = strContent.replace(r"\n", "")
            strContent = strContent.replace(r"\t", "")
            strContent = strContent.replace(r"\/", "/")
            strContent = strContent.replace(r'\"', "'")
            strContent = strContent.decode('unicode_escape')
            if strContent:
                strContent = strContent.replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", "")
            else:
                return ""
        except Exception:
            s=sys.exc_info()
            msg = (u"getPanelInfo Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
            return ""
        return strContent
