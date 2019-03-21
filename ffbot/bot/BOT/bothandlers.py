#coding=utf-8

import requests
import json
import random
import re
import traceback
import time
from .models import Class, Boss, NickBoss, NickClass
from .models import HeartBeat
from urllib.request import quote
from hashlib import md5
from selenium import webdriver
import os


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
    ret_msg = ('yukari,\ncopyright by 紫上\nyukari是一个机器人，主要用于方便玩ff14的狗群友查找相'
    '关资料\n框架思路借鉴于獭獭@Bluefissure\n代码来自@紫上\nlink: https://github.com/hahatianx/ffbot')
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
    /music:  网易云音乐找歌
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
    ff_url = 'https://www.fflogs.com/zone/statistics/table/{}/dps/{}/100/8/1\
    /100/1000/7/0/Global/{}/All/0/normalized/single/0/-1/'.format(quest_id, boss_id, class_name)
    r = requests.get(url=ff_url)
    per_list = [10, 25, 50, 75, 95, 99, ]
    pattern_mch = [re.compile('series{}'.format(x)\
                              +r'.data.push\([+-]?(0|([1-9]\d*))(\.\d+)?\)') for x in per_list]
    per_list.append(100)
    pattern_mch.append(re.compile('series'+r'.data.push\([+-]?(0|([1-9]\d*))(\.\d+)?\)'))
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
    if k_len == 1 and kargs[0] == 'help':
        ret_msg = '/dps指代帮助:\n'
        cls_obj = NickClass.objects.all()
        bos_obj = NickBoss.objects.all()
        ret_msg += '职业指代\n'
        for obj in cls_obj:
            ret_msg += '{}: {} -> {}\n'.format(obj.id, obj.nick_name, obj.class_id.name)
        ret_msg += 'BOSS指代\n'
        for obj in bos_obj:
            ret_msg += '{}: {} -> {}\n'.format(obj.id, obj.nick_name, obj.boss_id.name)
        ret_msg = ret_msg[:-1]
    elif k_len != 2:
        ret_msg = '你的指令好像用错了鸭\n正确用法:\n/dps <boss> <class>\nboss class具体指代表请查询/dps help'
    else:
        boss_nick, class_nick = kargs[0], kargs[1]
        ascii_fail = False
        if not isascii(boss_nick) or not isascii(class_nick):
            ret_msg = ('yukari比较懒，不想在/dps指令下看到非英文文字，就不想帮你查了\n'
                      '正确用法:\n/dps <boss> <class>\n'
                      'boss class具体指代表请查询/dps help')
            ascii_fail = True
        if not ascii_fail:
            class_obj = NickClass.objects.filter(nick_name=class_nick)
            boss_obj = NickBoss.objects.filter(nick_name=boss_nick)
            db_search_fail = False
            if len(boss_obj) == 0:
                ret_msg = 'yukari没有找到你指定的boss {} 的信息'.format(boss_nick)
                db_search_fail = True
            else:
                r_boss = boss_obj[0].boss_id
            if len(class_obj) == 0:
                if len(ret_msg) > 0:
                    ret_msg += '\n'
                ret_msg += 'yukari没有找到你指定的职业 {} 的信息'.format(class_nick)
                db_search_fail = True
            else:
                r_class = class_obj[0].class_id
            if not db_search_fail:
                day_index = (int(time.time()) - r_boss.add_time) // (24 * 3600)
                # print(day_index)
                try:
                    msg_dict = get_dps_list(r_boss.quest_id, r_boss.boss_id, r_class.name, day_index)
                    ret_msg = ('以下是国际服FFLOGS {} 在 {} 中第{}天'
                                '的dps表现:\n'.format(r_class.name, r_boss.name, day_index))
                    for k, v in msg_dict.items():
                        ret_msg += '%s%%: %.2f\n' % (k, v)
                    ret_msg = ret_msg[:-1]
                except:
                    traceback.print_exc()
                    ret_msg = '抓取出现bug，快叫紫上上出来挨打'
    return ret_msg


def MusicHandler(*kargs):
    if len(kargs) < 15:
        search_txt = ' '.join(kargs)
        driver_path = '/home/ffxiv/ffbot/chromedriver'
        os.environ["webdriver.chrome.driver"] = driver_path
        raw_music_url = 'https://music.163.com/#/search/m/?s={}&type=1'.format(search_txt)
        music_url = quote(raw_music_url, safe=';/?:@&=+$,#', encoding='utf-8')
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("window-size=1024,768")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(driver_path, port=9515, options=chrome_options)
        url_ok = True
        driver.set_page_load_timeout(5)
        try:
            driver.get(url=music_url)
        except:
            ret_msg = '网络出现了问题，yukari开始摸鱼了'
            url_ok = False
        if url_ok:
            driver.switch_to.frame('contentFrame')
            song_list = driver.find_elements_by_xpath("//div[starts-with(@class, 'item f-cb h-flag')]")
            if len(song_list) == 0:
                ret_msg = 'yukari找不到你想要的歌曲，不信你自己搜搜看\n' + music_url
            else:
                tar_song_ele = song_list[0]
                song_url = tar_song_ele.find_element_by_xpath(
                    "//div[@class='td w0']/div/div[@class='text']/a").get_attribute('href')
                song_name = tar_song_ele.find_element_by_xpath(
                    "//div[@class='td w0']").text
                artist_name = tar_song_ele.find_element_by_xpath(
                    "//div[@class='td w1']").text
                album_name = tar_song_ele.find_element_by_xpath(
                    "//div[@class='td w2']").text
                ret_msg = (
                    'yukari在网易云音乐为你找到了这首歌\n',
                    '歌曲名: {}\n'.format(song_name),
                    '艺术家: {}\n'.format(artist_name),
                    '专辑名: {}\n'.format(album_name),
                    song_url,
                )
        driver.quit()
    else:
        ret_msg = '指令好像用错了鸭\n正确用法：\n/music <name> [singer]'
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
        elif len(kargs) == 1 and kargs[0] == 'dove_prob':
            ret_msg = '现在的鸽子复读概率{}%'.format(self.prob * 100)
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


class Repeater(object):
    def __init__(self):
        self.last_msg = ''
        self.cnt = 0
        self.switch = True

    def run(self, kargs):
        digest = md5(' '.join(kargs).encode(encoding='utf-8')).hexdigest()
        if self.last_msg == digest:
            self.cnt += 1
            if self.cnt == 3 and self.switch:
                return ' '.join(kargs)
        else:
            self.last_msg = digest
            self.cnt = 1
        return ''

    def cmd_handler(self, kargs):
        if len(kargs) != 1:
            ret_msg = '复读开关指令有误'
        else:
            if kargs[0] in ['on', 'off']:
                self.switch = True if kargs[0] == 'on' else False
                ret_msg = '复读机已经被设置为 {}'.format('开' if self.switch else '关')
            else:
                ret_msg = '复读开关指令有误'
        return ret_msg


# mysql always disconnects with django for no valid operations within a period of time
# this class is aimed at keeping in touch with mysql through a periodical updating operation
# once coolq detects a message, the consumer.py calls this class to send a periodical update if the time's up
class MysqlHeartBeat(object):
    def __init__(self):
        self.time_out = 3600
        self.last_message = -1
        self.counter = 1

    def heartbeat(self):
        ret_msg = ''
        now_time = time.time()
        if self.last_message == -1 or \
           now_time > self.last_message + self.time_out:
            try:
                tar = HeartBeat.objects.filter(id=1)
                if len(tar) > 0:
                    tar.update(beats=self.counter)
                    self.counter += 1
                    self.last_message = now_time
                else:
                    ret_msg = '紫上上，heartbeat好像没有记录哟'
            except Exception as e:
                traceback.print_exc()
                ret_msg = str(e)
        return ret_msg

    def cmd_handler(self, *kargs):
        if len(kargs) == 1 and kargs[0] == 'check':
            return self.check()
        elif len(kargs) == 2 and kargs[0] == 'set_time_out':
            time_out = kargs[1]
            if time_out.isdigit():
                time_out = int(time_out)
                return self.set_time_out(time_out)
            else:
                ret_msg = 'set_time_out 第二个指令需要一个数字'
        else:
            ret_msg = '指令好像出现了错误'
        return ret_msg


    def set_time_out(self, time_out):
        if time_out > 28800 or time_out < 3600:
            ret_msg = '超时设置不能太高或者太低，(3600, 28800)最佳'
        else:
            self.time_out = time_out
            ret_msg = 'mysql 超时设置设定为:{}'.format(time_out)
        return ret_msg

    def check(self):
        try:
            tar = HeartBeat.objects.filter(id=1)
            if len(tar) > 0:
                ret_msg = '当前mysql HeartBeat Counter {}'.format(tar[0].beats)
            else:
                ret_msg = 'mysql HeartBeat 缺失，紫上上你怎么那么蠢'
        except Exception as e:
            traceback.print_exc()
            ret_msg = str(e)
        return ret_msg


if __name__ == '__main__':
    print(MusicHandler('Monkey Me', 'Mly'))
