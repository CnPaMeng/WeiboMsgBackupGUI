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
from model.images import AppIcon

class TaskBarIcon(wx.TaskBarIcon):
    ID_Minshow=wx.NewId()
    ID_Maxshow=wx.NewId()
    ID_Closeshow=wx.NewId()
    
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(AppIcon.GetIcon(), u'爬盟采集器')  #wx.ico为ico图标文件
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick) #定义左键双击
        self.Bind(wx.EVT_MENU, self.OnMinshow, id=self.ID_Minshow)
        self.Bind(wx.EVT_MENU, self.OnMaxshow, id=self.ID_Maxshow)
        self.Bind(wx.EVT_MENU, self.OnCloseshow, id=self.ID_Closeshow)

    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def OnMinshow(self,event):
        self.frame.Iconize(True)
  
    def OnMaxshow(self,event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def OnCloseshow(self,event):
        self.frame.OnCloseWindow(None)

    # 右键菜单
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_Maxshow, u'显示')
        menu.Append(self.ID_Minshow, u'最小化')
        menu.Append(self.ID_Closeshow, u'退出')
        return menu
        