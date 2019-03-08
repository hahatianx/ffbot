#coding=utf-8


def EchoHandler(*kargs):
    ret_msg = ''
    if len(kargs) != 1:
        ret_msg = '你的指令好像用错了鸭\n正确用法:\n/echo <string>'
    else:
        ret_msg = kargs[0]
    return ret_msg

