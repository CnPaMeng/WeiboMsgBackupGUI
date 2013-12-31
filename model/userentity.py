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
Created on 2012-3-29

@author: Zoe
'''
#顺序：自身ID，屏幕名，用户名，性别，地址，个人介绍，认证信息，是否加V，用户标签，
#头像地址，博客网址，用户建立时间，抓取时间，粉丝数，关注数，微博数，用户基本信息，
#用户教育信息，用户职业信息，用户关注的人的ID ,MSN, QQ
COLUMN_USERNAME = "un"
COLUMN_SCREENNAME = "sn"
COLUMN_SEX = "sx"
COLUMN_ADDRESS = "ad"
COLUMN_DESCRIPTION = "de"
COLUMN_BIRTHDAY = "bd"
COLUMN_PROFILE_IMAGE_URL = "iu"
COLUMN_FOLLOWERS_NUM = "an"
COLUMN_FRIENDS_NUM = "fn"
COLUMN_MSG_NUM = "mn"
COLUMN_ISVIP = "iv"
COLUMN_VERIFICATION_INFO = "vi"
COLUMN_CRAWL_TIME = "wt"
COLUMN_USER_TAG = "tg"
COLUMN_CREATE_TIME = "at"
COLUMN_USERERL_FOLLOWERS_IDS = "fui"#所有关注人的ID，中间以“，”隔开
COLUMN_ISDAREN = "dr"

COLUMN_EDUCATION = "edu"
COLUMN_WORK = "work"

COLUMN_QQ = "qq"
COLUMN_MSN = "msn"
COLUMN_EMAIL = "em"