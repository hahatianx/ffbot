#coding=utf-8

import requests
import json

def EchoHandler(*kargs):
    ret_msg = ''
    if len(kargs) != 1:
        ret_msg = '你的指令好像用错了鸭\n正确用法:\n/echo <string>'
    else:
        ret_msg = kargs[0]
    return ret_msg

def AboutHandler(*kargs):
    ret_msg = '''yukari,\ncopyright by 紫上\nyukari是一个机器人，主要用于方便玩ff14的狗群友查找相关资料\n框架思路借鉴于獭獭@Bluefissure\n全部代码来自@紫上
    '''
    return ret_msg

def NuannuanHandler(*kargs):
    ret_msg = ''
    try:
        r = requests.get(url='http://yotsuyu.yorushika.tk:5000')
        r = json.load(r.text)
        if r['success']:
            ret_msg = r['content']
            ret_msg += '\nPowered by 露儿[Yorushika]'
        else:
            ret_msg = 'An error occurred.'
    except Exception as e:
        ret_msg = 'Error %s' % str(e)
    return ret_msg

