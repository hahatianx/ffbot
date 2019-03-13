#coding=utf-8

import requests
import json
import random
import re
import traceback
import time
from .models import Class, Boss, NickBoss, NickClass
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
    ret_msg = '''yukari,\ncopyright by 紫上\nyukari是一个机器人，主要用于方便玩ff14的狗群友查找相关资料\n框架思路借鉴于獭獭@Bluefissure\n代码来自@紫上\nlink: https://github.com/hahatianx/ffbot
    '''
    return ret_msg


def HelpHandler(*kargs):
    ret_msg = '''
    /about:  作者信息
    /echo:   复读机
    /dress:  查看暖暖作业
    /search: 查找物品
    /raid:   查看raid攻略情况
    /tools:  辅助网站网址链接
    /dps:    查看FFLOGS高难本dps
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


raid_config_fd = open('/home/ffxiv/ffbot/ffbot/bot/BOT/raid_handler_config.json', 'r', encoding='utf-8')
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


def ToolsiteHandler(*kargs):
    ret_msg = '''
    素素攻略站: https://www.ffxiv.cn/
    捕鱼人(猫腹): http://cn.ff14angler.com/
    DPS警察: https://xivanalysis.com/
    团辅计算器: http://www.xivrdps.com/
    FF LOGS: https://www.fflogs.com/
    '''
    return ret_msg


def get_dps_list(quest_id, boss_id, class_name, day_index):
    ff_url = 'https://www.fflogs.com/zone/statistics/table/{}/dps/{}/100/8/1/100/1000/7/0/Global/{}/All/0/normalized/single/0/-1/'.format(quest_id, boss_id, class_name)
    r = requests.get(url=ff_url)
    per_list = [10, 25, 50, 75, 95, 99,]
    pattern_mch = [re.compile('series{}'.format(x)+r'.data.push\([+-]?(0|([1-9]\d*))(\.\d+)?\)') for x in per_list]
    day_index = max(0, day_index - 1)
    ret_dict = dict()
    for ptn, perc in zip(pattern_mch, per_list):
        target_tuple = ptn.findall(r.text)[day_index]
        dps_string = target_tuple[1] + target_tuple[2]
        dps_float = float(dps_string) if len(dps_string) > 0 else 0
        ret_dict[perc] = dps_float
    return ret_dict


def DpsHandler(*kargs):

    def isascii(t_str):
        return all(ord(c) < 128 for c in t_str)

    k_len = len(kargs)
    ret_msg = ''
    if k_len != 2:
        ret_msg = '你的指令好像用错了鸭\n正确用法:\n/dps <boss> <class>'
    else:
        boss_nick, class_nick = kargs[0], kargs[1]
        ascii_fail = False
        if not isascii(boss_nick) or not isascii(class_nick):
            ret_msg = 'yukari比较懒，不想在/dps指令下看到非英文文字，就不想帮你查了'
            ascii_fail = True
        class_obj = NickClass.objects.filter(nick_name=class_nick) if not ascii_fail else None
        boss_obj = NickBoss.objects.filter(nick_name=boss_nick) if not ascii_fail else None
        db_search_fail = False
        if boss_obj and len(boss_obj) == 0:
            ret_msg = 'yukari没有找到你指定的boss {} 的信息'.format(boss_nick)
            db_search_fail = True
        else:
            r_boss = boss_obj[0].boss_id
        if class_obj and len(class_obj) == 0:
            if len(ret_msg) > 0:
                ret_msg += '\n'
            ret_msg += 'yukari没有找到你指定的职业 {} 的信息'.format(class_nick)
            db_search_fail = True
        else:
            r_class = class_obj[0].class_id
        if not db_search_fail and not ascii_fail:
            day_index = (int(time.time()) - r_boss.add_time) // (24 * 3600)
            # print(day_index)
            try:
                msg_dict = get_dps_list(r_boss.quest_id, r_boss.boss_id, r_class.name, day_index)
                ret_msg = '以下是国际服FFLOGS {} 在 {} 中的dps表现:\n'.format(r_class.name, r_boss.name)
                for k, v in msg_dict.items():
                    ret_msg += '%s%%: %.2f\n' % (k, v)
                ret_msg = ret_msg[:-1]
            except:
                traceback.print_exc()
                ret_msg = '抓取出现bug'
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

