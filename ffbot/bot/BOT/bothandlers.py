#coding=utf-8

import requests
import json
import random
from urllib.request import quote


def EchoHandler(*kargs):
    ret_msg = ''
    if len(kargs) == 0:
        ret_msg = '你的指令好像用错了鸭\n正确用法:\n/echo <string>'
    else:
        for x in kargs:
            ret_msg += x
            ret_msg += ' '
        ret_msg = ret_msg[:-1]
    return ret_msg

def AboutHandler(*kargs):
    ret_msg = '''yukari,\ncopyright by 紫上\nyukari是一个机器人，主要用于方便玩ff14的狗群友查找相关资料\n框架思路借鉴于獭獭@Bluefissure\n全部代码来自@紫上\nlink: https://github.com/hahatianx/ffbot
    '''
    return ret_msg

def HelpHandler(*kargs):
    ret_msg = '''
    /about:  作者信息
    /echo:   复读机
    /dress:  查看暖暖作业
    /search: 查找物品
    /raid:   查看raid攻略情况
    emmm,目前只有那么多啦
    '''
    return ret_msg

def NuannuanHandler(*kargs):
    ret_msg = ''
    try:
        r = requests.get(url="http://yotsuyu.yorushika.tk:5000/")
        tx = json.loads(r.text)
        if tx['success']:
            ret_msg = tx['content']
            ret_msg += '\nby 露儿[Yorushika]'
        else:
            ret_msg = 'An error occurred.'
    except Exception as e:
        ret_msg = 'Error'
    return ret_msg

def SearchItemHandler(*kargs):
    if len(kargs) != 1:
        ret_msg = '你的指令好像用错了鸭\n正确用法:\n/search <item>'
    else:
        link = 'https://ff14.huijiwiki.com/wiki/ItemSearch?name=%s' % kargs[0]
        link = quote(link, safe=';/?:@&=+$,', encoding='utf-8')
        ret_msg = 'yukari在网上找呀找...\n搜索名：%s\n' % kargs[0]
        ret_msg += link
    return ret_msg

raid_config_fd = open('./raid_handler_config.json', 'r', encoding='utf-8')
raid_config_dict = json.load(raid_config_fd)

def get_raid_info(tar_url, tar_name, tar_server):
    ret_msg = ''
    tar_data = {
        'method': 'queryhreodata',
        'stage': 1,
        'name': tar_name,
        'areaID': 1,
        'groupID': tar_server,
    }
    r = requests.post(url=tar_url, data=tar_data)
    rep = json.loads(r.text)
    if rep['Code'] != 0:
        ret_msg += rep['Message']
    else:
        for lv in range(0, 4):
            tar_str = 'Level%s' % (lv + 1)
            date_time = rep['Attach'][tar_str]
            header_str = '第{}层: '.format(lv + 1)
            ret_msg += header_str
            if date_time is None or len(date_time) < 8:
                ret_msg += '找不到记录\n'
            else:
                ret_msg += '{}年{}月{}日\n'.format(date_time[:4], date_time[4:6], date_time[6:])
    return ret_msg


def RaidHandler(*kargs):
    print(raid_config_dict)
    if len(kargs) != 2:
        ret_msg = '你的指令好像用错了鸭\n正确用法:\n/raid <name> <server_name>'
    else:
        s_name, s_server = kargs[0], kargs[1]
        if s_server not in raid_config_dict:
            ret_msg = 'yukari好像找不到这个服务器，服务器名字要写全哦'
        else:
            ret_msg = '{}({})的欧米茄零式挑战记录如下:\n'.format(s_name, s_server)
            tar_lst = ['阿尔法幻境', '西格玛幻境', '德尔塔幻境']
            tar_server = raid_config_dict[s_server]['groupID']
            for raids in tar_lst:
                tar_url = raid_config_dict[raids]
                ret_msg += raids
                ret_msg += '\n'
                ret_msg += get_raid_info(tar_url, s_name, tar_server)
    return ret_msg


class Sheep(object):
    def __init__(self):
        self.prob = 0

    def handler(self, kargs):
        ret_msg = ''
        if len(kargs) > 1 and kargs[0] == 'set_prob':
            if kargs[1].isdigit():
                self.set_prob(kargs[1])
                ret_msg = '鸽子提醒复读概率: %s / 100' % kargs[1]
        else:
            flag = False
            for str_ in kargs:
                ret_msg += str_
                ret_msg += ' '
                if '鸽子' in str_:
                    flag = True
            if flag and random.random() < self.prob:
                ret_msg = ret_msg[:-1].replace('鸽子', '鸽羊')
            else:
                ret_msg = ''
        return ret_msg

    def set_prob(self, prob):
        self.prob = float(prob) / 100

