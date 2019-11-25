#coding=utf-8


from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
import gc
import logging
from bot.BOT.bothandlers import EchoHandler, AboutHandler, NuannuanHandler, SearchItemHandler, HelpHandler, \
    RaidHandler, ToolsiteHandler, DpsHandler, RandomHandler, MusicHandler, DressClawer, TimeHandler
from bot.BOT.bothandlers import Sheep, MysqlHeartBeat, Repeater
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)

LOGGER = logging.getLogger(__name__)
this_sheep = Sheep()
this_heartbeat = MysqlHeartBeat()
this_repeater = Repeater()
this_dressclawer = DressClawer()
this_timer = TimeHandler()

Handler_dict = {
    '/echo': EchoHandler,
    '/about': AboutHandler,
    '/dress': NuannuanHandler,
    '/search': SearchItemHandler,
    '/help': HelpHandler,
    '/raid': RaidHandler,
    '/tools': ToolsiteHandler,
    '/dps': DpsHandler,
    #'/music': MusicHandler,
    # for the reason that my server has limited memory, web browser can hardly be launched with mysql running
    '/random': RandomHandler,
    '/cmd_heartbeat': this_heartbeat.cmd_handler,
    '/cmd_repeater': this_repeater.cmd_handler,
    '/time': this_timer.timehandler,
}

class WSConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self):
        gc.collect()
        await self.close()

    # serialize msg to fit <http api for coolq>
    async def serialize(self, action, params):
        text_data = {
            'action': action,
            'params': params,
        }
        event = {'type': 'send.event', 'text': json.dumps(text_data)}
        await self.send(event['text'])

    async def send_message(self, is_private, tar_id, message):
        print(is_private, tar_id, message.encode('utf-8'))
        if is_private:
            await self.serialize('send_private_msg', {'user_id': tar_id, 'message': message})
        else:
            await self.serialize('send_group_msg', {'group_id': tar_id, 'message': message})

    async def process(self, msg):
        phase = 0
        try:
            plain_text = msg['message']
        except:
            LOGGER.ERROR('Process Unable to get message')
            phase |= 1
        try:
            msg_type = msg['message_type']
        except:
            LOGGER.ERROR('Message type not found')
            phase |= (1 << 1)
        try:
            target_id = msg['user_id'] if msg_type == 'private' else msg['group_id']
        except:
            LOGGER.ERROR('Message target not found')
            phase |= (1 << 2)
        if phase:
            return
        # print('process first-phase finished, phase code %d' % phase)
        (cmd_str, *kargs) = plain_text.split()
        if cmd_str in Handler_dict:
            return_msg = Handler_dict[cmd_str](*kargs)
            await self.send_message(msg_type == 'private', target_id, return_msg)

        ls = plain_text.split()
        # important: HeartBeat for mysql
        #####important#####
        #beat_message = this_heartbeat.heartbeat()
        #if len(beat_message) > 0:
            #await self.send_message(msg_type == 'private', target_id, beat_message)
        #####important#####
        if cmd_str == '/send':
            if kargs[0] == 'group' and kargs[1].isdigit():
                await self.send_message(False, kargs[1], ' '.join(kargs[2:]))

        # repeaters
        dove_flag = True
        if len(ls) > 0:
            repeater_msg = this_repeater.run(ls)
            if len(repeater_msg) > 0:
                dove_flag = False
                await self.send_message(msg_type == 'private', target_id, repeater_msg)

        # repeating doves
        #####special#####
        if len(ls) > 0:
            return_msg = this_sheep.handler(ls)
            if len(return_msg) > 0 and dove_flag:
                await self.send_message(msg_type == 'private', target_id, return_msg)
        #####special#####


    # 1) deserialize msg  2) handle msg 3) serialize msg 4) send
    async def receive(self, text_data):
        msg = json.loads(text_data)
        try:
            self.post_type = msg['post_type']
        except:
            LOGGER.error('Unable to get post_type')
            return
        if self.post_type == 'message':
            try:
                self.msg_type = msg['message_type']
                self.message = msg['message']
            except:
                LOGGER.error('Event message without Message')
                return
        if 'message' in msg.keys():
            await self.process(msg)

