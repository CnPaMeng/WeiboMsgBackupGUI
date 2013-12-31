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
Created on 2012-10-25

@author: Zoe
'''

import wx
import sys
from model import syscontext

class VerifyCodeFrame(wx.Frame):
    
    def __init__(self, parent, filename="pin.png"):
        try:
            wx.Frame.__init__(self, parent, title="Loading Verify Code")
            self.mainFrame = parent
            p = wx.Panel(self)
            fgs = wx.FlexGridSizer(cols=3, hgap=10, vgap=10)
            #1 从文件载入图像
            filename = (filename)
            img1 = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            # Scale the oiginal to another wx.Image
            w = img1.GetWidth()
            h = img1.GetHeight()
            img2 = img1.Scale(w*3, h*3)#2 缩小图像
            #3 转换它们为静态位图部件
            sb2 = wx.StaticBitmap(p, -1, wx.BitmapFromImage(img2))
            codeText = wx.TextCtrl(p, -1, "", size=(100, 50),style=wx.TE_PROCESS_ENTER)
            codeText.SetMaxLength(7)
            btn = wx.Button(p, label=u"Submit",size=(70, 50))
            btn.SetToolTipString(u"Please type verify code...")
            # and put them into the sizeri
            fgs.Add(sb2)
            fgs.Add(codeText)
            fgs.Add(btn)
            p.SetSizerAndFit(fgs)
            self.codeText = codeText
            self.btn = btn
            self.btn.Bind(wx.EVT_BUTTON, self.OnEnterCode, self.btn)
            self.Bind(wx.EVT_TEXT_ENTER, self.OnEnterCode, self.codeText)
            self.Bind(wx.EVT_CLOSE, self.OnClose)
            self.Fit()
        except:
            s=sys.exc_info()
            msg = (u"VerifyCodeFrame ERROR %s happened on line %d" % (s[1],s[2].tb_lineno))
            print msg
    
    def OnClose(self, event):
        wx.CallAfter(self.mainFrame.EnableLoginWin, True)
        genthread = syscontext.MAIN_GENTHREAD
        genthread.lock.acquire()
        genthread.lockcondition.notify()
        genthread.lock.release()
        self.Destroy()
    
    def OnEnterCode(self, event):
        code = self.codeText.GetValue()
        if len(code) >= 4:
            syscontext.VERIFY_CODE = code
            self.codeText.SetValue("")
            wx.CallAfter(self.mainFrame.EnableLoginWin, True)
            genthread = syscontext.MAIN_GENTHREAD
            genthread.lock.acquire()
            genthread.lockcondition.notify()
            genthread.lock.release()
            self.Destroy()
        else:
            event.Skip()

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frm = VerifyCodeFrame(None, "D:\zoe file\eclipse-python\WeiboCrawler\downloader\pin.png")
    frm.Center()
    frm.Show()
    app.MainLoop()
