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


import urllib2
import cookielib
import time
import datetime
import json
import re
import random
import urllib
import base64
import StringIO
import gzip
from model.log4py import Log4py
import sys
from model import syscontext
import os
import wx
import rsa
from rsa import transform

logger = Log4py().getLogger("run")


class LoginSinaCom():
    
    def __init__(self, **kwargs):
        #INIT cookie load object
        self.cj = cookielib.LWPCookieJar()
        self.cookie_support = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(self.cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)
        self.soft_path = kwargs.get("soft_path", "")
        self.cookiefile = os.path.join(self.soft_path, "cookie.dat")
        self.proxyip = kwargs.get("proxyip", "")
        self.pcid = ""
        self.servertime = ""
        self.nonce = ""
        self.pubkey = ''
        self.rsakv = ''
    
    
    def __get_millitime(self):
        """ get mill times """
        pre = str(int(time.time()))
        pos = str(datetime.datetime.now().microsecond)[:3]
        p = pre + pos
        return p
    
    
    def get_servertime(self, login_un):
        """ get sine server time """
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=account&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.2)&_=%s' % self.__get_millitime()
        result = {}
        servertime = None
        nonce = None
        headers = self.__get_headers()
        headers['Host'] = 'login.sina.com.cn'
        headers['Accept'] = '*/*'
        headers['Referer'] = 'http://weibo.com/'
        del headers['Accept-encoding']
        for i in range(3):  #@UnusedVariable
            req = self.pack_request(url, headers)
            data = urllib2.urlopen(req).read()
            p = re.compile('\((.*)\)')
            try:
                json_data = p.search(data).group(1)
                data = json.loads(json_data)
                servertime = str(data['servertime'])
                nonce = data['nonce']
                result["servertime"] = servertime
                result["nonce"] = nonce
                result["rsakv"] = str(data['rsakv'])
                result["pubkey"] = str(data['pubkey'])
                self.pcid = str(data['pcid'])
                break
            except:
                msg = u'Get severtime error!'
                logger.error(msg)
                continue
        return result
    
    
    def get_global_id(self):
        """ get sina session id """
        time = self.__get_millitime()
        url = "http://beacon.sina.com.cn/a.gif"
        headers = self.__get_headers()
        headers['Host'] = 'beacon.sina.com.cn'
        headers['Accept'] = 'image/png,image/*;q=0.8,*/*;q=0.5'
        headers['Referer'] = 'http://weibo.com/'
        req = self.pack_request(url, headers)
        urllib2.urlopen(req)
    

    def get_random_nonce(self, range_num=6):
        """ get random nonce key """
        nonce = ""
        for i in range(range_num):  #@UnusedVariable
            nonce += random.choice('QWERTYUIOPASDFGHJKLZXCVBNM1234567890')
        return nonce
    
    
    def dec2hex(self, string_num):
        base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A')+6)]
        num = int(string_num)
        mid = []
        while True:
            if num == 0: break
            num, rem = divmod(num, 16)
            mid.append(base[rem])
        return ''.join([str(x) for x in mid[::-1]])
    
    
    def get_pwd(self, pwd, servertime, nonce):
        #pwd1 = hashlib.sha1(pwd).hexdigest()
        #pwd2 = hashlib.sha1(pwd1).hexdigest()
        #pwd3_ = pwd2 + servertime + nonce
        #pwd3 = hashlib.sha1(pwd3_).hexdigest()
        #return pwd3
        p = int(self.pubkey, 16)
        pub_key  = rsa.PublicKey(p, int('10001', 16))
        pwd = '%s\t%s\n%s' % (servertime, nonce, pwd)
        pwd =  (self.dec2hex(transform.bytes2int(rsa.encrypt(pwd.encode('utf-8'), pub_key))))
        return pwd
    
    
    def get_user(self, username):
        username_ = urllib.quote(username)
        username = base64.encodestring(username_)[:-1]
        return username
    
    
    def save_verifycode(self, url):
        try:
            cookiestr = ""
            for cookie in self.cj.as_lwp_str(True, True).split("\n"):
                cookie = cookie.split(";")[0]
                cookie = cookie.replace("\"", "").replace("Set-Cookie3: ", " ").strip() + ";"
                cookiestr += cookie
            headers = {'Host': 'login.sina.com.cn',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1',
                       'Accept': 'image/png,image/*;q=0.8,*/*;q=0.5',
                       #'Accept-encoding': 'gzip, deflate',
                       'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                       'Connection': 'keep-alive',
                       'Referer'  :  'http://weibo.com/',
                       'Cookie'  :  cookiestr,
                      }
            req = self.pack_request(url, headers)
            response = urllib2.urlopen(req, timeout=10)
            content = response.read()
            f = open(os.path.join(self.soft_path, "pin.png"), "wb")
            f.write(content)
            f.flush()
            f.close()
        except:
            logger.error(u"save verify code error.")
    
    
    def login(self, login_un, login_pw):
        loginFalg = False
        try:
            try:
                stObj = self.get_servertime(login_un)
                self.servertime = stObj.get("servertime")
                self.nonce = stObj.get("nonce")
                self.pubkey = stObj.get("pubkey")
                self.rsakv = stObj.get("rsakv")
            except:
                return False
            #获取会话ID
            self.get_global_id()
            loginHtml = self.do_login(login_un, login_pw)
            loginHtml = loginHtml.replace('"', "'")
            #print loginHtml
            #p = re.compile('location\.replace\(\'(.*?)\'\)')
            try:
                p = re.compile('location\.replace\(\'(.*?)\'\)')
                login_url = p.search(loginHtml).group(1)
                #print login_url
                if "retcode=0" in loginHtml:
                    return self.redo_login(login_url)
                #是否需要手动输入验证码
                if syscontext.VERIFY_INPUT_FLAG:
                    logger.info(u"Allow user type verify code.")
                    pass
                else:
                    logger.error(u"Enable input verify code,return failure.")
                    return False
                #需要验证码，你妹
                if "retcode=5" in loginHtml:
                    logger.error(u"password or account error.")
                    return False
                if "retcode=4040" in loginHtml:
                    logger.error(u"do login too much times.")
                    return False
                #这次是真的要验证码：code 4049
                if "retcode=4049" in login_url:
                    for i in range(3):
                        logger.info(u"need verify code.")
                        verifycode_url = 'http://login.sina.com.cn/cgi/pin.php?r=%s&s=0&p=%s' % (random.randint(20000000,99999999), self.pcid)
                        self.save_verifycode(verifycode_url)
                        syscontext.VERIFY_CODE = ""
                        codeimg = os.path.join(os.path.join(syscontext.userentity.get("path", ""), syscontext.FILE_PATH_DEFAULT), "pin.png")
                        logger.info(u"verify code img path:%s." % codeimg)
                        try:
                            window = syscontext.MAIN_WINDOW
                            genthread = syscontext.MAIN_GENTHREAD
                            wx.CallAfter(window.EnableMainWin, False)
                            wx.CallAfter(window.ShowVerifyCode, codeimg)
                            #print "before self.acquire"
                            genthread.lock.acquire()
                            genthread.lockcondition.wait()
                            genthread.lock.release()
                            #print "after self.release"
                            #veroifyFrame = VerifyCodeFrame(window, filename=codeimg)
                            #veroifyFrame.Center()
                            #veroifyFrame.Show(True)
                            #app.MainLoop()
                        except:
                            s = sys.exc_info()
                            msg = (u"app error %s happened on line %d" % (s[1], s[2].tb_lineno))
                            logger.error(msg)
                        door = syscontext.VERIFY_CODE
                        logger.error(u"get input verify code:%s" % door)
                        #附加验证码再次登录
                        self.nonce = self.get_random_nonce()
                        loginHtml = self.do_login(login_un, login_pw, door=door)
                        loginHtml = loginHtml.replace('"', "'")
                        p = re.compile('location\.replace\(\'(.*?)\'\)')
                        if p.search(loginHtml):
                            login_url = p.search(loginHtml).group(1)
                            return self.redo_login(login_url)
                        else:
                            if "retcode=2070" in loginHtml:
                                #小LANG吃翔吧
                                logger.error(u"verify code:%s error." % door)
                                continue
                            else:
                                break
            except:
                s = sys.exc_info()
                msg = (u"do login %s happened on line %d" % (s[1], s[2].tb_lineno))
                logger.error(msg)
                loginFalg = False
        except Exception:
            s = sys.exc_info()
            msg = (u"login: %s happened on line %d" % (s[1], s[2].tb_lineno))
            logger.error(msg)
        return loginFalg
    
    
    def redo_login(self, login_url):
        try:
            headers = self.__get_headers()
            headers['Referer'] = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)'
            req = self.pack_request(login_url, headers)
            urllib2.urlopen(req)
            #self.cj.clear(name="Apache", domain=".sina.com.cn", path="/")
            #self.cj.clear(name="SINAGLOBAL", domain=".sina.com.cn", path="/")
            self.cj.save(self.cookiefile, True, True)
            msg = u'login success'
            logger.info(msg)
            loginFalg = True
        except:
            s = sys.exc_info()
            msg = (u"redo_login %s happened on line %d" % (s[1], s[2].tb_lineno))
            logger.error(msg)
            loginFalg = False
        return loginFalg
    
    
    def do_login(self, login_un, login_pw, door=""):
        try:
            loginFalg = False #登录状态
            username = login_un #微博账号
            pwd = login_pw #微博密码
            url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.2)'
            #POST DATA for login
            postdata = {
#                    'entry': 'weibo',
#                    'gateway': '1',
#                    'from': '',
#                    'savestate': '7',
#                    'userticket': '1',
#                    'ssosimplelogin': '1',
#                    'vsnf': '1',
#                    'vsnval': '',
#                    'su': '',
#                    'service': 'miniblog',
#                    'servertime': '',
#                    'nonce': '',
#                    'pwencode': 'wsse',
#                    'sp': '',
#                    'encoding': 'UTF-8',
#                    'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
#                    'returntype': 'META'
                    'entry': 'weibo',
                    'gateway': '1',
                    'from': '',
                    'savestate': '7',
                    'userticket': '1',
                    'pagerefer' : '',
                    'ssosimplelogin': '1',
                    'vsnf': '1',
                    'vsnval': '',
                    'service': 'miniblog',
                    'pwencode': 'rsa2',
                    'rsakv' : self.rsakv,
                    'encoding': 'UTF-8',
                    'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                    'returntype': 'META',
                    'prelt' : '26',
                }
            postdata['servertime'] = self.servertime
            postdata['nonce'] = self.nonce
            postdata['su'] = self.get_user(username)
            postdata['sp'] = self.get_pwd(pwd, self.servertime, self.nonce).lower()
            #当需要验证码登录的时候
            if door:
                postdata['pcid'] = self.pcid
                postdata['door'] = door.lower()
            #headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1'}
            headers = {'Host': 'login.sina.com.cn',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/17.0',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-encoding': 'gzip, deflate',
                       'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                       #'Accept-Charset': 'GB2312,utf-8;q=0.7,*;q=0.7',
                       'Connection': 'keep-alive',
                       'Referer'  :  'http://weibo.com/',
                       'Content-Type': 'application/x-www-form-urlencoded',
                      }
            req = self.pack_request(url, headers, postdata)
            result = urllib2.urlopen(req)
            #cj.save(cookiefile, True, True)
            if result.info().get("Content-Encoding") == 'gzip':
                text = self.gzip_data(result.read())
            else:
                text = result.read()
            return text
        except:
            s = sys.exc_info()
            msg = (u"do_login: %s happened on line %d" % (s[1], s[2].tb_lineno))
            logger.error(msg)
        return loginFalg
    
    
    def check_cookie(self, un, pw, softPath):
        loginFalg = True
        self.cookiefile = os.path.join(softPath, "cookie.dat")
        if os.path.exists(self.cookiefile):
            msg = u"cookie dat exist."
            logger.info(msg)
            if "Set-Cookie" not in open(self.cookiefile,'r').read():
                msg = u"but does not contain a valid cookie."
                logger.info(msg)
                loginFalg = self.login(un, pw)
        else:
            loginFalg = self.login(un, pw)
        if loginFalg:
            return self.valid_cookie()
        else:
            return False
    '''
    #当HTML参数为空时
    #需要在login调用之后执行
    #返回cookiestr or Flase
    '''
       
       
    def valid_cookie(self, html=""):
        #http://weibo.com/signup/signup
        html = str(html)
        if not html:
            headers = self.__get_headers()
            html = self.get_content_head(url="http://weibo.com/kaifulee", headers=headers)
        if not html:
            msg = u"need relogin."
            logger.error(msg)
            self.clear_cookiedat(self.cookiefile) #clear cookie file
            return False
        html = str(html)
        html = html.replace('"', "'")
        if "sinaSSOController" in html:
            p = re.compile('location\.replace\(\'(.*?)\'\)')
            #p = re.compile('location\.replace\("(.*?)"\)')
            try:
                login_url = p.search(html).group(1)
                headers = self.__get_headers()
                headers['Host'] = 'account.weibo.com'
                req = self.pack_request(url=login_url, headers=headers)
                result = urllib2.urlopen(req)
                #self.cj.clear(name="Apache", domain=".sina.com.cn", path="/")
                #self.cj.clear(name="SINAGLOBAL", domain=".sina.com.cn", path="/")
                self.cj.save(self.cookiefile, True, True)
                if result.info().get("Content-Encoding") == 'gzip':
                    html = self.gzipData(result.read())
                else:
                    html = result.read()
            except:
                msg = u"relogin failure."
                logger.error(msg)
                self.clear_cookiedat(self.cookiefile)
                return False
        if "违反了新浪微博的安全检测规则" in html:
            msg = u"cookie failure."
            logger.error(msg)
            self.clear_cookiedat(self.cookiefile) #clear cookie file
            return False
        elif "您的帐号存在异常" in html and "解除限制" in html:
            msg = u"账号被限制."
            logger.error(msg)
            self.clear_cookiedat(self.cookiefile)#clear cookie file
            return False
        elif "$CONFIG['islogin'] = '0'" in html:
            msg = u"登录失败."
            logger.error(msg)
            self.clear_cookiedat(self.cookiefile)#clear cookie file
            return False
        elif "$CONFIG['islogin']='1'" in html:
            #print "cookie success."
            msg = u"cookie success."
            logger.info(msg)
            #print cj.as_lwp_str(True, True).replace("\n", ";").replace("Set-Cookie3: ", " ").strip()
            #cokiestr = ""
            #for cookie in self.cj.as_lwp_str(True, True).split("\n"):
            #    if "Apache" in cookie or "SINAGLOBAL" in cookie:
            #        continue
            #    cookie = cookie.split(";")[0]
            #    cookie = cookie.replace("\"", "").replace("Set-Cookie3: ", " ").strip() + ";"
            #    cokiestr += cookie
            self.cj.save(self.cookiefile, True, True)
            return True
        else:
            msg = u"登录失败."
            self.clear_cookiedat(self.cookiefile)  #clear cookie file
            logger.error(msg)
            return False
    
    
    def get_content_head(self, url, headers={}, data=None):
        content = ""
        try:
            if os.path.exists(self.cookiefile):
                self.cj.revert(self.cookiefile, True, True)
                self.cookie_support = urllib2.HTTPCookieProcessor(self.cj)
                self.opener = urllib2.build_opener(self.cookie_support, urllib2.HTTPHandler)
                urllib2.install_opener(self.opener)
            else:
                return ""
            req = self.pack_request(url=url, headers=headers, data=data)
            #response = urllib2.urlopen(req, timeout=15)
            response = self.opener.open(req, timeout=10)
            if response.info().get("Content-Encoding") == 'gzip':
                content = self.gzip_data(response.read())
            else:
                content = response.read()
            #time.sleep(0.1*random.randint(10, 20))
        except urllib2.HTTPError, e:
            return e.code
        except:
            s=sys.exc_info()
            msg = u"get_content Error %s happened on line %d" % (s[1], s[2].tb_lineno)
            logger.error(msg)
            content = ""
        return content
    
    
    def get_content_cookie(self, url, headers={}, data=None):
        content = ""
        try:
            req = self.pack_request(url=url, headers=headers, data=data)
            opener = urllib2.build_opener(self.cookie_support)
            response = opener.open(req, timeout=10)
            if response.info().get("Content-Encoding") == 'gzip':
                content = self.gzip_data(response.read())
            else:
                content = response.read()
            #time.sleep(0.1*random.randint(10, 20))
        except:
            s=sys.exc_info()
            msg = u"get_content Error %s happened on line %d" % (s[1], s[2].tb_lineno)
            logger.error(msg)
            content = ""
        return content
    
    
    def clear_cookiedat(self, datpath):
        try:
            os.remove(datpath)
            #f = file(datpath, 'w')
            #f.truncate()
            #f.close()
        except:
            pass
    
    
    def pack_request(self, url="", headers={}, data=None):
        if data:
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            data = urllib.urlencode(data)
        req = urllib2.Request(
                url=url,
                data=data,
                headers=headers
            )
        proxyip = self.proxyip
        if proxyip and "127.0.0.1" not in proxyip:
            if proxyip.startswith("http"):
                proxyip = proxyip.replace("http://", "")
            req.set_proxy(proxyip, "http")
        return req
    

    def gzip_data(self, spider_data):
        """ get data from gzip """
        if 0 == len(spider_data):
            return spider_data
        spiderDataStream = StringIO.StringIO(spider_data)
        spider_data = gzip.GzipFile(fileobj=spiderDataStream).read()
        return spider_data
    
    
    def __get_headers(self):
        headers = {'Host': 'weibo.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:13.0) Gecko/20100101 Firefox/13.0.1',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-encoding': 'gzip, deflate',
                   'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
                   'Connection': 'keep-alive',
                  }
        return headers