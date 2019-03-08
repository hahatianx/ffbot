#coding=utf-8


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


