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

import ConfigParser
import os
from model.log4py import Log4py
import re

logger = Log4py().getLogger('CrawlerThread')

class UserConfig():
    
    def __init__(self, rootPath=""):
        self.config=ConfigParser.ConfigParser()
        self.rootPath = rootPath
        self.configPath = "file\\config.ini"
        
    def WriteUserConfig(self, _type, value):
        try:
            value = value.replace(r'\n', '')
            if self.rootPath != "":
                configFile = os.path.join(self.rootPath, self.configPath)
                if not os.path.exists(configFile):
                    f = file(configFile,"w")
                    f.close()
                content = open(configFile).read()
                #Window下用记事本打开配置文件并修改保存后，编码为UNICODE或UTF-8的文件的文件头
                #会被相应的加上\xff\xfe（\xff\xfe）或\xef\xbb\xbf，然后再传递给ConfigParser解析的时候会出错
                #，因此解析之前，先替换掉
                content = re.sub(r"\xfe\xff","", content)
                content = re.sub(r"\xff\xfe","", content)
                content = re.sub(r"\xef\xbb\xbf","", content)
                open(configFile, 'w').write(content)
                self.config.read(configFile)
                if not self.config.has_section(_type):   
                    self.config.add_section(_type)
                if value != "":
                    self.config.set(_type, "un", value)
                    #r+模式写入配置文件
                    self.config.write(open(configFile, "r+"))
            else:
                logger.error("SYS rootPath is empty.")
        except Exception, e:
            logger.error("Warn:write user config file has occur an error.%s" % e)
    
    def GetUserConfig(self, _type, option): #@ReservedAssignment
        configVal = ""
        try:
            if self.rootPath != "":
                configFile = os.path.join(self.rootPath, self.configPath)
                if os.path.exists(configFile):
                    content = open(configFile).read()
                    #Window下用记事本打开配置文件并修改保存后，编码为UNICODE或UTF-8的文件的文件头
                    #会被相应的加上\xff\xfe（\xff\xfe）或\xef\xbb\xbf，然后再传递给ConfigParser解析的时候会出错
                    #，因此解析之前，先替换掉
                    content = re.sub(r"\xfe\xff","", content)
                    content = re.sub(r"\xff\xfe","", content)
                    content = re.sub(r"\xef\xbb\xbf","", content)
                    open(configFile, 'w').write(content)
                    self.config.read(configFile)
                    if self.config.has_section(_type):
                        configVal = self.config.get(_type, option)
            else:
                logger.error("SYS rootPath is empty.")
                return None
        except Exception, e:
            logger.error("Warn:read user config file has occur an error.%s" % e)
            return None
        configVal = configVal.replace(r'\n', '')
        return configVal

if __name__ == '__main__':
    config = UserConfig("D:\zoe file\eclipse-python\WeiboCrawlerMsgGUI_py")
    un = config.GetUserConfig("sysuser", "un")
    print "un:",un
    
    