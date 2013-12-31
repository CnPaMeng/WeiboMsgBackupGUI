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
from model.mainaction import MainAction
from frame.mainframe import MainFrame
import sys
from model.userconfig import UserConfig
from model import syscontext
from model.images import AppIcon
from model.startimg import StartImg
import win32con
import wx.lib.agw.hyperlink as hl
from frame.verifycodeframe import VerifyCodeFrame

class LoginFrame(wx.Frame):
    
    def __init__(self, parent, id, title, framesize): #@ReservedAssignment
        try:
            self.mainAction = MainAction()
            wx.Frame.__init__(self, parent, id, title, size=framesize,
                              style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER |wx.MAXIMIZE_BOX))
            loginPanel = wx.Panel(self)
            box = wx.StaticBox(loginPanel, -1, "")
            bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
            
            self.config = UserConfig(syscontext.userentity["path"])
            
            unLabel = wx.StaticText(loginPanel, -1, u"微博用户：")
            pwLabel = wx.StaticText(loginPanel, -1, u"微博密码：")
            unText = wx.TextCtrl(loginPanel, -1, self.config.GetUserConfig("sysuser", "un"), size=(200, -1))
            pwText = wx.TextCtrl(loginPanel, -1, "", size=(200, -1), style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
            
            inputSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
            inputSizer.Add(unLabel, 0)
            inputSizer.Add(unText, 2)
            inputSizer.Add(pwLabel, 0)
            inputSizer.Add(pwText, 2)
            
            bsizer.Add(inputSizer, 0, wx.TOP|wx.ALIGN_CENTER, 10)
            
            submitBtn = wx.Button(loginPanel, label=u"登录",size=(100, 35))
            cancelBtn = wx.Button(loginPanel, label=u"取消",size=(100, 35))
            buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
            buttonSizer.Add(submitBtn, 1, wx.RIGHT, 1)
            buttonSizer.Add(cancelBtn, 1, wx.LEFT, 1)
            
            self._hyper1 = hl.HyperLinkCtrl(loginPanel, wx.ID_ANY, u"[微博消息采集器]爬萌网址:www.cnpameng.com",
                                            URL="http://www.cnpameng.com/")
            
            border = wx.BoxSizer(wx.VERTICAL)
            border.Add((15,15), 0)
            border.Add(bsizer, 2, wx.ALIGN_CENTER, 25)
            border.Add((15,15), 0)
            border.Add(buttonSizer, 2, wx.ALIGN_CENTER, 25)
            border.Add(self._hyper1, 1, wx.ALIGN_CENTER, 5)
            
            loginPanel.SetSizer(border)
            loginPanel.Fit()
            loginPanel.Enable()
            
            self.loginPanel = loginPanel
            
            self.Fit()
            border.SetSizeHints(self)
            
            self.unText = unText
            self.pwText = pwText
            self.submitBtn = submitBtn
            self.cancelBtn = cancelBtn
            self.Bind(wx.EVT_BUTTON, self.StartLogin, submitBtn)
            self.Bind(wx.EVT_BUTTON, self.Cancel, cancelBtn)
            
            self.Bind(wx.EVT_TEXT_ENTER, self.KeyPress, pwText)
            self.regHotKey()
            self.Bind(wx.EVT_HOTKEY, self.handleHotKey, id=self.hotKeyId)
        except:
            s=sys.exc_info()
            msg = (u"Login frame Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            return False
    def regHotKey(self):
        """
        This function registers the hotkey Ctrl + F12 with id
        """
        self.hotKeyId = wx.NewId()
        self.RegisterHotKey(
            self.hotKeyId, #a unique ID for this hotkey
            win32con.MOD_CONTROL, #the modifier key
            win32con.VK_F12) #the key to watch for
        
    def handleHotKey(self, evt):
        if self.ConfirmDialog(u"确定开启Debug模式?!将会记录程序详细运行日志.") == wx.ID_YES:
            syscontext.userentity["debug"] = True
    
    def KeyPress(self, event):
        self.StartLogin(None)
        
    def StartLogin(self, event):
        try:
            username = self.unText.GetValue().strip()
            password = self.pwText.GetValue().strip()
            if username == "" or password == "":
                self.ShowMessage(u"用户名/密码不能为空!", wx.ICON_WARNING)
                return False
            self.config.WriteUserConfig("sysuser", username)
            self.EnableLoginWin(False)
            self.mainAction.Login(self, username, password)
        except:
            s=sys.exc_info()
            self.ShowMessage((u"StartLogin Error %s happened on line %d" % (s[1],s[2].tb_lineno)), wx.ICON_INFORMATION)
    
    def ShowVerifyCode(self, filename=""):
        self.veroifyFrame = VerifyCodeFrame(self, filename=filename)
        self.veroifyFrame.Center()
        self.EnableLoginWin(False)
        self.veroifyFrame.Show(True)
    
    def EnableLoginWin(self, enableFlag):
        if enableFlag:
            self.loginPanel.Enable()
        else:
            self.loginPanel.Disable()
    
    def ConfirmDialog(self, msg):
        dlg = wx.MessageDialog(self, msg,
                      'System Prompt', wx.YES_NO | wx.ICON_EXCLAMATION)
        retCode = dlg.ShowModal()
        dlg.Destroy()
        return retCode
        
    def Login(self, loginValid):
        try:
            if loginValid == "ok":
                self.Destroy()
                #添加启动图片
                wx.SplashScreen(StartImg.GetBitmap(), wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                1000, None, -1)
                wx.Yield()
                #创建框架
                frame = MainFrame(parent=None, id= wx.NewId(), title=u'微博备份神器[爬盟版]', framesize=(800,450)) 
                frame.SetIcon(AppIcon.GetIcon())
                frame.Center()
                frame.Show(True)
            elif loginValid == "versionError":
                self.ShowMessage(u"采集器版本过低，请到爬萌资源网站下载最新的采集器!<www.cnpameng.com>", wx.ICON_ERROR)
            else:
                self.ShowMessage(u"登录失败:%s" % loginValid, wx.ICON_ERROR)
        except Exception:
            s=sys.exc_info()
            msg = (u"Login Error %s happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            #print e
    
    def Cancel(self, event):
#        self.unText.SetValue("")
#        self.pwText.SetValue("")
        self.Destroy()
    
    def ShowMessage(self, message, style):
        msgDlg = wx.MessageDialog(None, message,
                               u'系统提示',
                               wx.OK | style
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        msgDlg.ShowModal()
        msgDlg.Destroy()
        