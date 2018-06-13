#coding=utf8
__author__ = 'WYK'

import os
import time
import logging
import requests
import itchat
import threading

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

# KEY = '8edce3ce905a4c1dbb965e6b35c3834d'
KEY = 'f26276bebeba492ab763e83e89c511d0'

auto_rep = True
no_auto_rep_list = []
time_interval = True

class LOG:
    def __init__(self):

        self.LOG_HOME = r'D:\log\wxRobotLog'
        if not os.path.exists(self.LOG_HOME):
            os.makedirs(self.LOG_HOME)
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename=os.path.join(self.LOG_HOME, 'wxRobot.log'),
            filemode='w')
        self.set_file('default')

    def set_file(self, user):
        self.user = user

    def log(self, message):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print now
        print message
        logging.info(message)
        with open(os.path.join(self.LOG_HOME, self.user + '.log'), 'a') as f:
            f.write(now)
            f.write('\n')
            f.write(message)
            f.write('\n')

logger = LOG()

def ctl_msg(msg):
    global auto_rep, no_auto_rep_list, time_interval
    if msg['ToUserName'] != 'filehelper':
        return False
    print '!!!this is admin!!!'
    print 'msg:'
    print msg['Text']

    if msg['Text'] == 'open':
        auto_rep = True
        itchat.send(u'机器人已开启', 'filehelper')
    elif msg['Text'].startswith('open '):
        user = msg['Text'][5:]
        if user in no_auto_rep_list:
            no_auto_rep_list.remove(user)
        itchat.send(u'机器人已对 %s 开启' % user, 'filehelper')
    elif msg['Text'] == 'close':
        auto_rep = False
        itchat.send(u'机器人已关闭', 'filehelper')
    elif msg['Text'].startswith('close '):
        user = msg['Text'][6:]
        if user not in no_auto_rep_list:
            no_auto_rep_list.append(user)
        itchat.send(u'机器人已对 %s 关闭' % user, 'filehelper')
    elif msg['Text'] == 'list':
        print no_auto_rep_list
        itchat.send('已关闭列表：', 'filehelper')
        itchat.send(','.join(no_auto_rep_list), 'filehelper')
    elif msg['Text'].startswith('delay '):
        ctrl = msg['Text'][6:]
        if ctrl == 'open':
            time_interval = True
            itchat.send(u'延时回复已开启', 'filehelper')
        elif ctrl == 'close':
            time_interval = False
            itchat.send(u'延时回复已关闭', 'filehelper')
    elif msg['Text'] == 'auther':
        itchat.send(u'wechat-robot auther:君莫思归', 'filehelper')
    return True

def get_response(msg, userid = 'wechat-robot'):
    # 这里我们就像在“3. 实现最简单的与图灵机器人的交互”中做的一样
    # 构造了要发送给服务器的数据
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : KEY,
        'info'   : msg,
        'userid' : userid,
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
        return r.get('text')
    # 为了防止服务器没有正常响应导致程序异常退出，这里用try-except捕获了异常
    # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
    except:
        # 将会返回一个None
        return

# 这里是我们在“1. 实现微信消息的获取”中已经用到过的同样的注册方法
@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    global logger, no_auto_rep_list
    if ctl_msg(msg):
        return
    to_user_nickname = msg['User'].get('NickName', 'unknown')
    if not auto_rep or (to_user_nickname != 'unknown' and to_user_nickname in no_auto_rep_list):
        return

    # 为了保证在图灵Key出现问题的时候仍旧可以回复，这里设置一个默认回复
    defaultReply = 'I received: ' + msg['Text']
    # 如果图灵Key出现问题，那么reply将会是None
    reply = get_response(msg['Text'], to_user_nickname)
    # a or b的意思是，如果a有内容，那么返回a，否则返回b
    # 有内容一般就是指非空或者非None，你可以用`if a: print('True')`来测试
    try:
        logger.set_file(to_user_nickname)
        logger.log('%s:%s' % (to_user_nickname, msg['Text']))
        logger.log('rep:%s' % reply if reply else defaultReply)
    except Exception as e:
        print str(e)
        print "Exception ignored!!!!"

    if time_interval:
        sec = min(len(reply or defaultReply), 50)
        print "sec", sec
        def repl():
            itchat.send(reply or defaultReply, msg['FromUserName'])
            print "repled"
        t = threading.Timer(sec, repl)
        t.start()
    else:
        return reply or defaultReply

def main():
    # 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
    itchat.auto_login(hotReload=True)
    # print itchat.get_chatrooms(update=True)
    itchat.run()

try:
    main()
    print 'end!!!!!'
except Exception as e:
    print str(e)
    os.system('pause')

