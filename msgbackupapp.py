#!/usr/bin/python
#-*- encoding: utf-8 -*-

# This file is part of the Pameng, 
# Pameng website: http://www.cnpameng.com/,
# Sina weibo: http://weibo.com/cnpameng.

# This file is part of WeiboMsgBackup.

# Copyright (C) 2013 Pameng.
# Pameng <pameng.cn@gmail.com>, 2013.

# WeiboMsgBackup is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# WeiboMsgBackup is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with WeiboMsgBackup; see the file COPYING3.  If not see
# <http://www.gnu.org/licenses/>.
'''
Created on 2012-3-14
中文文件名时 需要相应处理
@author: Zoe
'''
import wx
import os
import sys
from model import syscontext
from model.images import AppIcon

reload(sys)
sys.setdefaultencoding('utf8') #@UndefinedVariable

class MainApp(wx.App):
    
    def __init__(self, redirect=True, filename=None):
        wx.App.__init__(self, redirect, filename)
        from model.mainaction import MainAction
        self.mainAction = MainAction()
        
    def OnInit(self):
        try:
            path=sys.argv[0][0:sys.argv[0].rfind('\\')+1]
            if self.check_chinese_path(path):
                wx.MessageBox(u"请在英文目录下启动采集器.")
                return False
            file_path = os.path.join(path,syscontext.FILE_PATH_DEFAULT)
            if not os.path.exists(file_path):
                os.mkdir(file_path)
            syscontext.userentity["path"] = path
            syscontext.userentity["debug"] = False
            from frame.loginframe import LoginFrame
            frame = LoginFrame(None, -1,u"使用SINA微博用户登录",(400,375))
            frame.SetIcon(AppIcon.GetIcon())
            frame.CenterOnScreen()
            frame.Show(True)
            return True
        except:
            #self.ShowMessage(u"Crawler error,case:%s" % e, wx.ICON_ERROR)
            s=sys.exc_info()
            msg = (u"Init Error (可能是配置文件被损坏.删除file文件夹config.ini重新运行采集器) %s happened on line %d" % (s[1],s[2].tb_lineno))
            wx.MessageBox(msg)
            return False
    
    def OnExit(self):
        self.Destroy()
    
    def check_chinese_path(self, path):
        if len(path) != len(unicode(path,'gb2312')):
            return True
        else:
            return False
       
if __name__ == '__main__':
    try:
        app = MainApp(redirect=False)
        #设置当所有窗口关闭时进程退出
        app.SetExitOnFrameDelete(True)
        app.MainLoop()  #2 进入主事件循环
    except:
        msg = u"初始化异常!请确保在英文目录下运行该程序."
        wx.MessageBox(msg)
