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
Created on 2012-3-30

@author: Zoe
'''
import logging
from model import syscontext
import os
import time

class Log4py(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.logPath = os.path.join(syscontext.userentity.get("path", ""),
                                    syscontext.FILE_PATH_DEFAULT)
        
    def getLogger(self, clazzName):
        dayDate = str(time.strftime("%Y-%m-%d"))
        self.logName = dayDate
        logLevel = logging.DEBUG
        logFileName = os.path.join(self.logPath,
                                   ("%s_%s_run.log" % (clazzName,self.logName)))
        logging.basicConfig(level=logLevel,
                            format='%(asctime)s %(levelname)s %(message)s',
                            filename=logFileName,
                            filemode='a')
        return logging.getLogger(clazzName)
    
    def debugMsg(self, msg):
        self.getLogger("DEBUG").debug(msg)
        
if __name__ == '__main__':        
    logger = Log4py().getLogger('log4py')
    logger.debug('test')
    