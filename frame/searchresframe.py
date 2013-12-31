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
 

import wx
from wx import html
import json
from model.userentity import *
import sys
from model.log4py import Log4py
from model import syscontext

log = Log4py()
logger = log.getLogger('run')

class SearchResFrame(wx.Frame):
    def __init__(self, parent, title ,userData=None):
        wx.Frame.__init__(self, parent, -1, title, size=(600,500))
        self.parent = parent
        #self.CreateStatusBar()
        html = MyHtmlWin(self, parent)
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()
        html.SetRelatedFrame(self, self.GetTitle() + " -- %s") #关联HTML到框架
        #html.SetRelatedStatusBar(0) #关联HTML到状态栏
        htmlStr = self.ParseData2Html(userData)
        wx.CallAfter(html.SetPage, htmlStr)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
    
    def OnCloseWindow(self, event):
        wx.CallAfter(self.parent.EnableMainWin, True)
        self.Destroy()
    
    def ParseData2Html(self, userData):
        htmlStr = ""
        try:
            if not userData:
                htmlStr = u"<h2>获取搜索结果失败</h2><hr/>请检查您的网络状态."
            else:
                if userData == "failure" or userData == "error":
                    htmlStr = u"<h2>未搜索到结果</h2><hr/>您搜索的用户不存在."
                else:
                    resultObj = json.loads(userData)
                    flag = resultObj.get("fg", -1)
                    if flag == -1:
                        userLst = resultObj.get("users", [])
                        htmlStr = u"<h3>搜索结果:[点击头像选定采集用户]</h3><hr><div>"
                        for user in userLst:
                            sex = user['sx']
                            if sex == "m":
                                sex = "男"
                            elif sex == "f":
                                sex = "女"
                            htmlStr += u'''<div><div><a href=\"%s\"><img src=\"%s\"></a>&nbsp;&nbsp;昵称： %s\t性别 ：%s\t<br>地区：%s\t%s</div><p>%s</p></div></div>
                            ''' % (user["uid"]+"_._"+user.get('sn'), user[COLUMN_PROFILE_IMAGE_URL].replace("/180/", "/50/"), user.get('sn'), sex, user['ad'], user['num'], user[COLUMN_DESCRIPTION])
                            htmlStr += "<hr/>"
                        htmlStr += u"</div>"
                    else:
                        htmlStr = u"<h2>未搜索到结果</h2><hr/>您搜索的用户不存在or状态异常."
        except Exception:
            s=sys.exc_info()
            msg = (u"ParseData2Html Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            logger.error(msg)
        return htmlStr

class MyHtmlWin(html.HtmlWindow):
    def __init__(self, parent, mainFrame):
        html.HtmlWindow.__init__(self, parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.parent = parent
        self.mainFrame = mainFrame
    
    def OnLinkClicked(self, linkinfo):
        #print linkinfo.GetHref()
        infos =  linkinfo.GetHref().split("_._")
        if infos and len(infos)>=2:
            msg = u"选择了用户 :%s" % infos[1]
            wx.CallAfter(self.mainFrame.WriteLog, msg)
            syscontext.tempentity["CRAWLERUID"] = [infos[0]]
            wx.CallAfter(self.mainFrame.EnableMainWin, True)
            self.parent.Destroy()
        else:
            msg = u"无效的链接 :%s" % str(infos)
            wx.CallAfter(self.mainFrame.WriteLog, msg)

