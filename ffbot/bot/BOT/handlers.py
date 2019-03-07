#coding=utf-8


def EchoHandler(*kargs):
    if len(kargs) == 1:
        return kargs[0]
    else:
        msg = '/echo使用方法错误\n/echo <\'...\'>'
        return msg
