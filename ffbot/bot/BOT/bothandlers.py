#coding=utf-8

local_debug = True

import requests
import json
import random
import re
import traceback
import time, datetime
if not local_debug:
    from .models import Class, Boss, NickBoss, NickClass
    from .models import HeartBeat
else:
    import rsa, binascii
    import http.cookiejar
    import base64
    import urllib
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    cj = http.cookiejar.LWPCookieJar()
    cookie_support = urllib.request.HTTPCookieProcessor(cj)
    opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
from urllib.request import quote
from hashlib import md5
from lxml import html



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
    /random: 随机数
    /time:   转换时间
    点歌 <歌名> [歌手]  这个API来自coolq论坛用户cs3248
    emmm,目前只有那么多啦
    '''
    return ret_msg


def NuannuanHandler(*kargs):
    ret_msg = ''
    try:
        r = requests.get(url="http://nuannuan.yorushika.co:5000/", timeout=5)
        tx = json.loads(r.text)
        if tx['success']:
            ret_msg = tx['content']
            ret_msg += '\nPowered by 露儿[Yorushika]'
        else:
            ret_msg = 'An error occurred.'
    except Exception as e:
        ret_msg = traceback.format_exc()
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


if not local_debug:
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
    r = requests.post(url=tar_url, data=tar_data, timeout=5)
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
    采集时钟: https://caiji.ffxiv.cn/
    配方计算器: http://v6.ffxiv.xin/
    生产模拟器: http://viktorlab.net/crafter/
    housing: http://ff14housing.com/
    配装模拟器: http://ffxiv.ariyala.com/
    '''
    return ret_msg


def get_dps_list(quest_id, boss_id, class_name, day_index):
    ff_url = 'https://www.fflogs.com/zone/statistics/table/{}/dps/{}/100/8/1\
    /100/1000/7/0/Global/{}/All/0/normalized/single/0/-1/'.format(quest_id, boss_id, class_name)
    # f_url = 'https://www.fflogs.com/zone/statistics/table/{}/dps/{}/{}/8/{}\
    # /100/1000/7/{}/Global/{}/All/0/normalized/single/0/-1/?keystone=15&dpstype={pdps}'.format(
    #     quest_id,
    #     boss_id,
    #     class_name,
    # )
    r = requests.get(url=ff_url, timeout=5)
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
                    s_list = []
                    for k in msg_dict.keys():
                        s_list.append(int(k))
                    s_list.sort(reverse=True)
                    for k in s_list:
                        v = msg_dict[k]
                        ret_msg += '%d%%: %.2f\n' % (k, v)
                    ret_msg = ret_msg[:-1]
                except:
                    ret_msg = '抓取出现bug，快叫紫上上出来挨打\n'
                    ret_msg += traceback.format_exc()
    return ret_msg


def RandomHandler(*kargs):
    random_dict = {
        'num': 1,
        'min': 0,
        'max': 99,
        'col': 1,
        'base': 10,
        'format': 'html',
        'rnd': 'new',
    }
    r_ok = True
    if len(kargs) == 1:
        tar = kargs[0]
        if tar.isdigit() and int(tar) < 100000:
            random_dict['max'] = int(tar)
        else:
            ret_msg = '上限设置有误，必须是一个小于1e5的非负整数\n/random [max]'
            r_ok = False
    elif len(kargs) == 2:
        t_num, t_max = kargs[0], kargs[1]
        if not t_num.isdigit() or not t_max.isdigit():
            ret_msg = '参数设置错误，num需要一个1e2以内的正整数，max需要一个1e5以内的非负整数\n/random [num] [max]'
            r_ok = False
        elif int(t_num) > 100 or int(t_max) > 100000:
            ret_msg = '参数设置错误，num需要一个1e2以内的正整数，max需要一个1e5以内的非负整数\n/random [num] [max]'
            r_ok = False
        else:
            random_dict['max'] = int(t_max)
            random_dict['num'] = int(t_num)
            random_dict['col'] = int(t_num)
    if r_ok:
        request_url = 'https://www.random.org/integers/?' \
                  + '&'.join('{}={}'.format(k, v) for k, v in random_dict.items())
        rcv_msg = requests.get(url=request_url, timeout=5)
        if rcv_msg.status_code == 200:
            page_node = html.etree.HTML(rcv_msg.text)
            tar_node = page_node.xpath(".//pre[@class='data'] | .//pre[@class='data']/following-sibling::*[1]")
            nums = tar_node[0].text.split()
            ret_msg = '以下是在random.org上随机出来的数字\n'
            cnt = 0
            for num in nums:
                if cnt and cnt % 5 == 0:
                    ret_msg += '\n'
                cnt += 1
                ret_msg += '%6d' % int(num)
            ret_msg += '\n' + tar_node[1].text
        else:
            ret_msg = str(rcv_msg)
    return ret_msg


def MusicHandler(*kargs):
    if len(kargs) < 15:
        tar_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36',
            "Content-Type": "text/html; charset=UTF-8",}
        tar_url = 'http://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={}&type=1&offset=0&total=true&limit=1'\
        .format(' '.join(kargs))
        rev_msg = requests.get(url=tar_url, headers=tar_header, timeout=5)
        print(rev_msg.text)
        rev_msg = json.loads(rev_msg.text)
        if 'result' in rev_msg:
            rev_msg = rev_msg['result']
            print(rev_msg)
            song_id = rev_msg['songs'][0]['id']
            artist_list = rev_msg['songs'][0]['artists']
            album_name = rev_msg['songs'][0]['album']['name']
            artist_name = ' '.join(x['name'] for x in artist_list)
            ret_msg = '[CQ:music,type=163,id={}]'.format(song_id)
            ret_msg += '\n艺术家: {}'.format(artist_name)
            ret_msg += '\n专辑名: {}'.format(album_name)
        else:
            ret_msg = 'yukari好像没有找到这首歌'
    else:
        ret_msg = '指令好像用错了鸭\n正确用法：\n/music <name> [singer]'
    return ret_msg


class TimeHandler(object):
    def __init__(self):
        self.daylighttime = 0

    def timehandler(self, *kargs):
        zone = [0, 8, -8, 9]
        zname = ['UTC', 'UTC+8', 'PST', 'JST']
        dst = {'utc': 1, 'utc+8': 0, 'pst': 1, 'jst': 0}
        tzone = {'utc': 0, 'pst': -8, 'utc+8': 8, 'jst': 9}
        def format_time(utcunixtime, cut=False):
            ret = []
            for n, z in zip(zname, zone):
                c_unixtime = utcunixtime + datetime.timedelta(hours=z)\
                             + datetime.timedelta(hours=self.daylighttime * dst[n.lower()])
                if cut:
                    ret.append('{:6}'.format(n) + ' : ' + c_unixtime.strftime('%Y-%m-%d %H:%M:%S')[11:])
                else:
                    ret.append('{:6}'.format(n) + ' : ' + c_unixtime.strftime('%Y-%m-%d %H:%M:%S'))
            return ret

        if len(kargs) == 0:
            cur_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=-self.daylighttime)
            str_time = format_time(cur_time)
            ret_msg = '转换时间:\n' + '\n'.join(str_time)
        elif kargs[0] == 'help':
            # print helping message
            ret_msg ='''yukari 的时区小工具:
    /time 打印当前时间
    /time HH:MM Zone 打印规定时区的时间
    /time YYYY-mm-dd HH:mm Zone 打印指定日期的时间'''
        elif kargs[0] == 'set_daylighttime':
            self.daylighttime = 1 if kargs[1] == '1' else 0
            ret_msg = '夏令时设置为{}'.format(self.daylighttime)
        elif len(kargs) == 2:
            # print time + zone
            tt_zone = kargs[1].lower()
            if tt_zone in tzone:
                d_dst = dst[tt_zone]
                ds = tzone[tt_zone]
                try:
                    tar_time = datetime.datetime.strptime(kargs[0], '%H:%M')\
                               + datetime.timedelta(days=5) + datetime.timedelta(hours=-ds)\
                               + datetime.timedelta(hours=d_dst * -self.daylighttime)
                    str_time = format_time(tar_time, True)
                    ret_msg = '转换时间:\n' + '\n'.join(str_time)
                except:
                    ret_msg = 'yukari 发现输入的数据有问题，请检查输入'
            else:
                ret_msg = 'yukari 发现输入的数据有问题，请检查输入'
        elif len(kargs) == 3:
            # date + time
            tt_zone = kargs[2].lower()
            if tt_zone in tzone:
                ds = tzone[tt_zone]
                d_dst = dst[tt_zone]
                try:
                    tar_time = datetime.datetime.strptime(kargs[0] + ' ' + kargs[1], '%Y-%m-%d %H:%M') \
                               + datetime.timedelta(hours=-ds) + datetime.timedelta(hours=d_dst * -daylighttime)
                    str_time = format_time(tar_time)
                    ret_msg = '转换时间:\n' + '\n'.join(str_time)
                except:
                    ret_msg = 'yukari 发现输入的数据有问题，请检查输入'
            else:
                ret_msg = 'yukari 发现输入的数据有问题，请检查输入'
        else:
            # bad format
            ret_msg = 'yukari 发现输入的数据有问题，请检查输入'
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


class DressClawer(object):
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'
        }
        self.time_out = datetime.datetime.now()
        self.status = False
        self.info = ''
        self.ID = [1750802063]
        self.host = 'https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100606&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&'
        self.ID_URL = self.get_urls()

    def post_data(self, url, data):
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'}
        data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url, data, headers)
        response = urllib.request.urlopen(request)
        text = response.read().decode('gbk')
        return text

    def get_data(self, url):
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        text = response.read()
        return text

    def get_urls(self):
        ID_urls = {}
        for id in range(len(self.ID)):
            urls = []
            urls.append(self.host + "page=1" + "&pagebar=0&id=" + str(self.ID[id]))
            for j in range(0, 2):
                urls.append(self.host + "page=" + str(1) + "&pagebar=" + str(j) + "&id=" + str(
                    self.ID[id]) + "&pre_page=" + str(1))
            ID_urls[id] = urls
        return ID_urls

    def login_weibo(self, nick, pwd):
        session = requests.session()
        prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.15)&_=1400822309846' % nick
        preLogin = session.get(prelogin_url).text
        servertime = re.findall('"servertime":(.*?),', preLogin)[0]
        pubkey = re.findall('"pubkey":"(.*?)",', preLogin)[0]
        rsakv = re.findall('"rsakv":"(.*?)",', preLogin)[0]
        nonce = re.findall('"nonce":"(.*?)",', preLogin)[0]

        su = base64.b64encode(bytes(urllib.request.quote(nick), encoding='utf-8'))
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)
        message = bytes(str(servertime) + '\t' + str(nonce) + '\n' + str(pwd), encoding='utf-8')
        sp = binascii.b2a_hex(rsa.encrypt(message, key))

        param = {'entry': 'weibo', 'gateway': 1, 'from': '', 'savestate': 7, 'useticket': 1,
                 'pagerefer': 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D',
                 'vsnf': 1, 'su': su, 'service': 'miniblog', 'servertime': servertime, 'nonce': nonce,
                 'pwencode': 'rsa2', 'rsakv': rsakv, 'sp': sp, 'sr': '1680*1050',
                 'encoding': 'UTF-8', 'prelt': 961,
                 'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'}

        s = self.post_data('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)', param)
        #urll = re.findall("location.replace\(\'(.*?)\'\);", s)
        print('login ok')

    def _craw_new_info(self):
        #self.login_weibo('shuhan.x.shen@gmail.com', 'shen123')
        user_url = 'https://m.weibo.cn/api/container/getIndex?containerid=1076031750802063'
        text_url = 'https://weibo.com/p/aj/mblog/getlongtext?mid={}'
        ret_dict = {
            'status': 'failure',
            'time': '',
            'text': '',
        }
        try:
            r = requests.get(url=user_url)
            content = json.loads(r.text).get('data')
            cards = content.get('cards')
            for c in cards:
                if c.get('card_type') == 9:
                    mblog = c.get('mblog')
                    pub_time = mblog.get('created_at')
                    pub_text = mblog.get('text')
                    reg_finder = re.compile('本周时尚品鉴 100点得分搭配：')
                    if len(reg_finder.findall(pub_text)) > 0:
                        tar_mid = mblog.get('mid')
                        tar_url = text_url.format(tar_mid)
                        rr = requests.get(url=tar_url, headers=self.header)
                        p_content = json.loads(rr.text)
                        raw_html = p_content.get('data').get('html')
                        if len(raw_html) > 0:
                            raw_text = ''
                            page_node = html.etree.HTML(raw_html)
                            l = page_node.xpath(".//*")
                            for x in l:
                                raw_text += x.tail + '\n' if x.tail is not None else ''
                            ret_dict['text'] = raw_text.replace('None', '')
                            ret_dict['time'] = pub_time
                            ret_dict['status'] = 'success'
                        break
        except Exception:
            ret_dict['text'] = traceback.format_exc()
        self.info = ret_dict
        print(json.dumps(ret_dict))

    def handler(self):
        a, b = self.get_dress()
        return self.wrap_info(a, b)

    def wrap_info(self, p_time, text):
        if p_time == '-1':
            ret_msg = 'yukari坏掉了！！！\n' + text
        else:
            ret_msg = 'yukari在微博上找到了呜呜栗子的暖暖攻略\n发布时间: {}\n\n'.format(p_time) + text + '\n'
            ret_msg += '信息来源：微博呜呜栗子 https://weibo.com/wuwulizi\n'
            ret_msg += '挑战时间截至{}，请快点加油啊！'.format(self.time_out)
        return ret_msg

    def get_dress(self):
        r = time.time() + 3600 * 8
        n_time = datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r)), '%Y-%m-%d %H:%M:%S')
        if (not self.status) or n_time > self.time_out or (self.info.get('status', 'failure') == 'failure'):
            self._craw_new_info()
            self.cal_next_unix_timeout()
            self.status = True
        if self.info.get('status', 'failure') == 'success':
            return self.info.get('time'), self.info.get('text')
        else:
            return '-1', self.info.get('text')

    def cal_next_unix_timeout(self):
        if self.status:
            time_delta = datetime.timedelta(days=7)
            now_datetime = self.time_out
            next_date = now_datetime + time_delta
            self.time_out = next_date
        else:
            r = time.time() + 3600 * 8
            r_localtime = time.localtime(r)
            base_time = datetime.datetime.strptime(time.strftime('%Y-%m-%d', r_localtime) + ' 16:00:00', '%Y-%m-%d %H:%M:%S')
            one_day = datetime.timedelta(days=1)
            while base_time.weekday() != 1:
                base_time += one_day
            self.time_out = base_time


if __name__ == '__main__':
    timeh = TimeHandler()
    print(timeh.timehandler('set_daylighttime', '1'))
    print(timeh.timehandler())
