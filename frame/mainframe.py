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
import sys

from model.mainaction import MainAction
from model.log4py import Log4py
from wx.lib import platebtn
from wx.lib.wordwrap import wordwrap
from model import syscontext
from model.userconfig import UserConfig
from frame.taskbarpanle import TaskBarIcon
from frame.searchresframe import SearchResFrame
from model.stcrawlthread import StartCrawlThread

wildcard = "DAT files|*.dat|"     \
           "All files (*.*)|*.*"

log = Log4py()
logger = log.getLogger('MainFrame')

class MainFrame(wx.Frame):
    
    def __init__(self, parent, id, title, framesize): #@ReservedAssignment
        try:
            wx.Frame.__init__(self, parent, id, title, size=framesize,
                              style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER |wx.MAXIMIZE_BOX))
            self.userConfig = UserConfig(syscontext.userentity["path"])
            self.createMainPanel()
            #绑定窗口的关闭事件
            self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
            #定义采集方式，0：MU版，1：SEARCH版
            self.CRAWLER_TYPE = 1
            #0未开始 1正在采集
            self.CRAWLER_STATUS = 0
            #定义主ACTION
            self.mainAction = MainAction()
            #定义是否采集登录用户标志
            self.CRAWLER_SELF = 0
            self.threads = []
            self.taskPath = syscontext.userentity["path"]+"\\file"
            self.resultPath = ""
            self.keepRunning = True
            self.crawlerCount = 1
            self.taskBarIcon = TaskBarIcon(self)
            self.processRangeVal = 0
            
            self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
            
        except Exception:
            #self.ShowMessage(u"Exception:%s" % str(e), wx.ICON_INFORMATION)
            s=sys.exc_info()
            msg = (u"Main Error '%s' happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            logger.error(u"Main Error:%s" % str(msg))
    
    def createMainPanel(self):
        try:
            mainPanel = wx.Panel(self)
            northSizer = self.createNorthPanel(mainPanel)
            savePathSizer = self.createSavePathPanel(mainPanel)
            centerSizer = self.createCenterPanel(mainPanel)
            southSizer = self.createSouthPanel(mainPanel)
            
            mainSizer = wx.BoxSizer(wx.VERTICAL)
            mainSizer.Add(northSizer, 0, wx.ALL, 5)
            
            mainSizer.Add(wx.StaticLine(mainPanel), 0,
                    wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
            
    #        mainSizer.Add(fileSizer, 0, wx.ALL, 5)
            mainSizer.Add(savePathSizer, 0, wx.ALL, 5)
            
            mainSizer.Add(centerSizer, 0, wx.ALL, 5)
            
            mainSizer.Add(wx.StaticLine(mainPanel), 0,
                    wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
            
            mainSizer.Add(southSizer, 0, wx.ALL, 5)
            
            mainPanel.SetSizer(mainSizer)
            mainSizer.Fit(mainPanel)
            mainSizer.SetSizeHints(self)
            self.mainPanel = mainPanel
            mainPanel.Enable()
            userentity = syscontext.userentity
            self.WriteLog("Running...")
            self.WriteLog(u"当前登录用户：%s"%userentity['un'])
            self.WriteLog(u"当前采集器版本：%s"%syscontext.CRAWLER_VERSION)
            if syscontext.userentity.get("debug", False):
                self.WriteLog(u"Debug模式.")
        except Exception:
            #self.ShowMessage(u"Exception:%s" % str(e), wx.ICON_INFORMATION)
            s=sys.exc_info()
            msg = (u"Main Error '%s' happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            logger.error(u"Main Error:%s" % str(msg))
        
    def createNorthPanel(self, panel):
        try:
            #创建画板
    #        northPanel = wx.Panel(mainPanel)
            #将按钮添加到画板
            userentity = syscontext.userentity
            
            crawlerBtn = wx.Button(panel, label=u"开始采集",size=(200, 35))
            helpBtn = platebtn.PlateButton(panel, -1, u"帮助？", None)
            userLabel = wx.StaticText(panel, -1, u"用户：")
            userBtn = platebtn.PlateButton(panel, -1, userentity['un'], None)
            userBtn.SetToolTipString(u"用户信息,采集记录显示...")
            
            northSizer = wx.BoxSizer(wx.HORIZONTAL)
            northSizer.Add(crawlerBtn, 2)
            northSizer.Add(helpBtn, 0, wx.ALIGN_CENTER)
            northSizer.Add(userLabel, 0, wx.ALIGN_CENTER | wx.RIGHT)
            northSizer.Add(userBtn, 1, wx.ALIGN_CENTER)
            
            #绑定按钮的单击事件
            crawlerBtn.Bind(wx.EVT_BUTTON, self.StartCrawler, crawlerBtn)
            helpBtn.Bind(wx.EVT_BUTTON, self.ShowHelpInfo, helpBtn)
            self.crawlerBtn = crawlerBtn
        except Exception:
            s=sys.exc_info()
            msg = (u"Main Error '%s' happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            logger.error(u"Main Error:%s" % str(msg))
        return northSizer

    def createSavePathPanel(self, panel):
        saveBtn = wx.Button(panel, label=u"选择结果路径",size=(100, 35))
        saveBtn.SetToolTipString(u"程序默认运行目录<file>为结果保存路径...")
        savePathText = wx.TextCtrl(panel, -1, self.userConfig.GetUserConfig("save", "un"), size=(300, -1))
        savePathText.SetEditable(False)
        savePathSizer = wx.BoxSizer(wx.HORIZONTAL)
        savePathSizer.Add(saveBtn, 0)
        savePathSizer.Add((10,5),0, wx.EXPAND)
        savePathSizer.Add(savePathText, 1, wx.CENTER)
        saveBtn.Bind(wx.EVT_BUTTON, self.ShowSaveChoice, saveBtn)
        self.savePathText = savePathText
        
        self.saveBtn = saveBtn
        
        return savePathSizer

    def createCenterPanel(self, panel):
        try:
            #for bottom sizer:
            slider = wx.Slider(panel, wx.NewId(), 5, 1, 20, pos=wx.DefaultPosition,
                               size=(250, -1),
                               style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
            slider.SetLineSize(10)
            slider.SetTickFreq(5, 1)
            st = wx.StaticText(panel, -1, u"开启线程数(推荐5):", (45, 15))
            
            webPanel = wx.Panel(panel)
            muPanel = wx.Panel(panel)
            #for top sizer:
            webBtn = wx.Button(panel, label=u"用户昵称/ID",size=(100, 35))
            webBtn.SetToolTipString(u"切换-->搜索采集方式:请输入需要采集的用户昵称 或者 用户ID搜索!")
            muCrawlBtn = wx.Button(panel, label=u"批量采集",size=(100, 35))
            muCrawlBtn.SetToolTipString(u"切换-->批量采集方式:请输入需要采集的用户ID列表，以英文\",\"(逗号)分割!")
            btnSzier = wx.BoxSizer(wx.VERTICAL)
            btnSzier.Add(webBtn, 0)
            btnSzier.Add(muCrawlBtn, 0)
            
            self.webBtn = webBtn
            self.muCrawlBtn = muCrawlBtn
            
            webBtn.Disable()
            muCrawlBtn.Enable()
            webBtn.Show(True)
            muCrawlBtn.Show(True)
            
            webUNText = wx.SearchCtrl(webPanel, size=(300,-1), style=wx.TE_PROCESS_ENTER)
            userCkBox = wx.CheckBox(webPanel, -1, u"采集自己")
            searchBtn = wx.Button(webPanel, label=u" 搜索 ",size=(100, 27))
            self.webUNText = webUNText
            self.userCkBox = userCkBox
            self.searchBtn = searchBtn
            
            webInputSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
            webInputSizer.Add(webUNText, 2)
            webInputSizer.Add(searchBtn, 2)
            webInputSizer.Add(userCkBox, 1)
            webInputSizer.Add((30,30), 2)
            webPanel.SetSizer(webInputSizer)
            webPanel.Show(True)
            
            uidsText = wx.TextCtrl(muPanel, -1, "" , size=(300, 70),
                             style = wx.TE_MULTILINE
                             #| wx.TE_RICH
                             | wx.TE_RICH2
                             )
            #descLabel = wx.StaticText(muPanel, -1, u"批量采集方式:\n请输入需要采集\n的用户ID列表;\n以英文\",\"(逗号)分割!")
            self.uidsText = uidsText
            
            muInputSizer = wx.BoxSizer(wx.HORIZONTAL)
            muInputSizer.Add(uidsText, 2)
            #muInputSizer.Add(descLabel, 0)
            muPanel.SetSizer(muInputSizer)
            muPanel.Show(False)
            
            inputSizer = wx.BoxSizer(wx.VERTICAL)
            inputSizer.Add((5,5), 0)
            inputSizer.Add(webPanel, 0)
            inputSizer.Add(muPanel, 0)
            
            self.webPanel = webPanel
            self.muPanel = muPanel
            self.inputSizer = inputSizer
            
            box = wx.StaticBox(panel, -1, u"采集进度")
            #采集当前进度/总请求次数，初始0
            self.finishedCount = 0
            self.curCount = 0
            self.totalCount = 0
            
            processBar = wx.Gauge(panel, -1, 100, (20, 50), (300, 25))
            processBar.SetBezelFace(3)
            processBar.SetShadowWidth(3)
            boxSizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
    #        t = wx.StaticText(box, -1, "RUNNING...")
            boxSizer.Add(processBar, 0, wx.TOP|wx.LEFT, 1)
            self.processBar = processBar
            
            sliderSizer =  wx.BoxSizer(wx.VERTICAL)
            sliderSizer.Add(st, 0)
            sliderSizer.Add(slider, 0)
            
            bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
            bottomSizer.Add(sliderSizer, 0)
            bottomSizer.Add((10, 10), 0)
            bottomSizer.Add(boxSizer, 2)
            
            topSizer = wx.BoxSizer(wx.HORIZONTAL)
            topSizer.Add(btnSzier, 0)
            topSizer.Add((10,5), 0)
            topSizer.Add(inputSizer, 0)
            
            centerSizer = wx.BoxSizer(wx.VERTICAL)
            
            centerSizer.Add(topSizer, 1, wx.EXPAND)
            centerSizer.Add((10,10), 0, wx.EXPAND)
            centerSizer.Add(bottomSizer, 1, wx.EXPAND)
            
            #bind event
            webBtn.Bind(wx.EVT_BUTTON, self.OnWebBtnClick, webBtn)
            searchBtn.Bind(wx.EVT_BUTTON, self.OnSearch, searchBtn)
            muCrawlBtn.Bind(wx.EVT_BUTTON, self.OnMuBtnClick, muCrawlBtn)
            self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.webUNText)
            self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.webUNText)
            self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox, userCkBox)
            self.centerSizer = centerSizer
            self.slider = slider
        except Exception:
            s=sys.exc_info()
            msg = (u"Main Error '%s' happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            logger.error(u"Main Error:%s" % str(msg))
        return centerSizer

    def createSouthPanel(self, panel):
        st = platebtn.PlateButton(panel, -1, u"清空日志", None)
        logText = wx.TextCtrl(panel, -1, "" , size=(600, 300),
                         style = wx.TE_MULTILINE
                         #| wx.TE_RICH
                         | wx.TE_RICH2
                         )
        logText.SetEditable(False)
        self.logText = logText
        southSizer = wx.BoxSizer(wx.VERTICAL)
        southSizer.Add(st, 0)
        southSizer.Add(logText, 0)
        st.Bind(wx.EVT_BUTTON, self.ClearLog, st)
        return southSizer

    #for action
    def OnIdle(self, event):
        self.count = self.count + 1
        if self.count == 100:
            self.count = 0
        self.processBar.SetValue(self.count)
        
    def OnCloseWindow(self, event):
        if self.ConfirmDialog(u'Are you sure to Exit?!') == wx.ID_YES:
            self.taskBarIcon.Destroy()
            self.Destroy()
    
    def OnIconfiy(self, event):
        self.Hide()
        event.Skip()
    
    def EnableMainWin(self, flag):
        if flag:
            self.mainPanel.Enable()
        else:
            self.mainPanel.Disable()
    
    def OnMuBtnClick(self, event):
        self.CRAWLER_TYPE = 0
        self.webBtn.Enable()
        self.muCrawlBtn.Disable()
        self.webPanel.Show(False)
        self.muPanel.Show(True)
        self.inputSizer.Detach(self.webPanel)
        self.inputSizer.Layout()
    
    def OnWebBtnClick(self, event):
        self.CRAWLER_TYPE = 1
        #self.ShowMessage(u'请输入需要采集的用户昵称 或者 用户ID...')
        #self.OnSearch(None)
        self.webBtn.Disable()
        self.muCrawlBtn.Enable()
        self.muPanel.Show(False)
        self.webPanel.Show(True)
        self.inputSizer.Detach(self.muPanel)
        self.inputSizer.Layout()
    
    def ShowHelpInfo(self, event):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = "Crawler Client"
        info.Version = syscontext.CRAWLER_VERSION
        info.Copyright = "(C) 2012 Programmers and Coders Everywhere"
        info.Description = wordwrap(
            u"1.爬萌SINA微博用户消息采集器；"
            u"\n2.采集方式1：输入sina微博用户昵称/用户ID进行搜索," 
            u"\n在搜索结果界面,点击头像选择需要采集的用户,开始采集;" 
            u"\n4.采集方式2：选择批量采集,输入用英文逗号分割的sina微博用户ID,最多为10;"
            u"\n5.更多采集资源可在爬萌资源网站下载：访问<Home page>。",
            350, wx.ClientDC(self))
        info.WebSite = ("http://114.113.145.13/", "Home page")
        info.Developers = [ "Trace,Thz,Zoe" ]
        wx.AboutBox(info)
    
    def ShowSaveChoice(self, event):
        
        dlg = wx.DirDialog(self, u"请选择保存任务结果文件的路径...",
                           style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.resultPath = dlg.GetPath()
            self.WriteLog(u"任务结果文件保存路径: %s" % (self.resultPath))
            self.savePathText.SetValue(self.resultPath)
        dlg.Destroy()
    
    def OnSearch(self, event):
        searchName = self.webUNText.GetValue().strip().encode("utf-8")
        if searchName == "":
            self.ShowMessage(u"请输入用户昵称 或者 用户ID搜索...")
        else:
#            if str.isdigit(nickname):
#                print "ID"
#            else:
#                print "nickname"
            self.mainAction.SearchWeibocnUser(searchName, self)
    
    def ShowSearchRes(self, data):
        self.searchFrame = SearchResFrame(self, u"搜索结果", userData=data)
        self.searchFrame.Center()
        self.EnableMainWin(False)
        self.searchFrame.Show(True)
    
    def OnCheckBox(self, event):
        status = event.IsChecked()
        self.CRAWLER_SELF = status
        if status:
            self.webBtn.Disable()
            self.webUNText.Disable()
            self.muCrawlBtn.Disable()
            self.searchBtn.Disable()
        else:
            #self.webBtn.Enable()
            self.webUNText.Enable()
            self.muCrawlBtn.Enable()
            self.searchBtn.Enable()
    
    def StartCrawler(self , event):
        try:
            if self.CRAWLER_SELF:
                self.WriteLog(u"采集当前登录用户...")
            if self.CRAWLER_TYPE == 0:
                uids = str(self.uidsText.GetValue().strip())
                if "," not in uids:
                    wx.MessageBox(u"未找到可执行的批量采集用户ID.")
                    return False
                else:
                    uidLst =  uids.split(",")
                    if len(uidLst) > 10:
                        wx.MessageBox(u"超出批量采集范围(最多为 10个用户)!")
                        return False
                    else:
                        syscontext.tempentity["CRAWLERUID"] = uidLst
            #print syscontext.tempentity.get("CRAWLERUID", None)
            if not self.CRAWLER_SELF and not syscontext.tempentity.get("CRAWLERUID", None):
                wx.MessageBox(u"未选定用户采集微博消息!")
                return False
            else:
                self.UpdateBtnLabel(u"停止采集")
                self.LockOptPanel(True)
                self.WriteLog(u"validating...")
                self.UpdateCrawlProcess(2)
                stThread = StartCrawlThread(1, self, event)
                stThread.start()
                #stThread.stop()
        except Exception:
            s=sys.exc_info()
            msg = (u"Exception %s happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            logger.error(msg)
    
    def OnCrawlerStop(self, event):
        if self.ConfirmDialog(u'采集进行中，确定要强行终止吗?!(当前采集数据会丢失)') == wx.ID_YES:
            self.WriteLog(u"监测到采集停止操作!")
            self.WriteLog(u"线程结束ing...")
            self.keepRunning = False
            self.StopThreads()
            self.UpdateBtnLabel(u"开始采集")
            self.LockOptPanel(False)
            self.CRAWLER_STATUS = 1
        
    def LockOptPanel(self, flag):
        if flag:
            self.webUNText.Disable()
            #self.webPWText.Disable()
            self.slider.Disable()
            self.saveBtn.Disable()
            self.webBtn.Disable()
            self.muCrawlBtn.Disable()
            self.searchBtn.Disable()
        else:
            self.webUNText.Enable()
            #self.webPWText.Enable()
            self.slider.Enable()
            self.saveBtn.Enable()
            if self.CRAWLER_TYPE:
                self.muCrawlBtn.Enable()
            else:
                self.webBtn.Enable()
            self.searchBtn.Enable()
            self.userCkBox.SetValue(False)
            
    def UpdateBtnLabel(self, labelStr):
        self.crawlerBtn.SetLabel(labelStr)
                
    def ConfirmDialog(self, msg):
        dlg = wx.MessageDialog(self, msg,
                      'System Prompt', wx.YES_NO | wx.ICON_EXCLAMATION)
        retCode = dlg.ShowModal()
        dlg.Destroy()
        return retCode
    
    def ShowMessage(self, message):
        msgDlg = wx.MessageDialog(self, message,
                               'System Prompt',
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        msgDlg.ShowModal()
        msgDlg.Destroy()
    
    def StopThreads(self):#从池中删除线程
        while self.threads:
            thread = self.threads[0]
            thread.stop()
            self.threads.remove(thread)
    
    #更新采集 进度条
    def UpdateCrawlProcess(self, processVal):
        self.processBar.SetValue(processVal)
        
    def SetCrawlProcessRange(self, rangeVal):
        self.processRangeVal = rangeVal
        #print "rangeVal: %s" % rangeVal
        self.processBar.SetRange(rangeVal+27)
    
    def ReInit(self):
        self.finishedCount = 0
        self.curCount = 0
        self.totalCount = 0
        self.UpdateCrawlProcess(0)
        self.keepRunning = True
        self.processRangeVal = 0
     
    def ThreadFinished(self, thread):#删除线程
        try:
            self.threads.remove(thread)
        except Exception:
            logger.error(u"线程被终止,采集结束!")
            self.WriteLog(u"线程被终止,采集结束!")
            
    def WriteLog(self, log):
        rows = self.logText.GetNumberOfLines()
        #MAX ROWS 500
        if rows > 500:
            self.logText.Clear()
        lastPos = self.logText.GetLastPosition()
        self.logText.SetInsertionPoint(lastPos)
        self.logText.WriteText(log+"\n")
    
    def ClearLog(self, event):
        self.logText.Clear()
        