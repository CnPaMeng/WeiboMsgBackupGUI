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
Created on 2012-3-21
系统上下文
@author: Zoe
'''
userentity={}
#是否强制要求用户录入微博登录信息
userRequired = True
#是否采集用户关注列表
userAttnLstCrawl = False

FILE_PATH_DEFAULT = "file"

CRAWLER_VERSION = "3.0.13"

#user ui type
#2 : 体验版
#1 ：标准版
USER_UI_TYPE_TRIAL = "2"
USER_UI_TYPE_NORMAL = "1"
USER_UI_TYPE_LATEST = "3"
#CRAWLERUID
#sina微博消息采集的用户ID
tempentity = {}

#默认不弹出验证码
VERIFY_INPUT_FLAG = 1

VERIFY_CODE = ""

MAIN_WINDOW = None
MAIN_GENTHREAD = None

LOGIN_SINA_COM = None
    
