#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'WYK'

import itchat
import traceback
import time
import os

robot_instance_num = 0

help_info = '''“new” 新登录-微信自动回复机器人
“auther” 作者信息'''

def ctl_msg(msg):
    global help_info
    if msg['ToUserName'] != 'filehelper':
        return False
    print '!!!this is admin!!!'
    print 'msg:'
    print msg['Text']

    if msg['Text'] == 'new':
        itchat.send(u'新登录', 'filehelper')
        os.system('mkdir -p robot_from_backend/%d;cd robot_from_backend/%d;nohup python /home/pi/code/wechat_robot/selfWechatRobot.py > log 2>&1 &' % (robot_instance_num, robot_instance_num))
        for i in range(5):
            if os.path.exists('robot_from_backend/%d/QR.png' % robot_instance_num):
                break
            itchat.send(u'请稍等...%d' % i, 'filehelper')
            time.sleep(1)
        itchat.send_image('robot_from_backend/%d/QR.png' % robot_instance_num, 'filehelper')
    elif msg['Text'] == 'auther':
        itchat.send(u'wechat-robot auther:君莫思归', 'filehelper')
    elif msg['Text'] == 'help':
        itchat.send(help_info, 'filehelper')
    return True

@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    if ctl_msg(msg):
        return

def main():
    #itchat.auto_login(hotReload=True, enableCmdQR=True)
    itchat.auto_login(hotReload=True, enableCmdQR=False)
    itchat.run()

if __name__ == '__main__':
    while True:
        try:
            main()
            print 'end!!!!!'
        except Exception as e:
            print str(e)
            print traceback.format_exc()
            time.sleep(5)
        print '!!!!!!restart!!!!!!!!'
