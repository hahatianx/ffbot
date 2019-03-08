#coding=utf-8


from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
import gc
import logging
from bot.BOT.handlers import EchoHandler
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)

LOGGER = logging.getLogger(__name__)

Handler_dict = {
    '/echo': EchoHandler,

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
        event = {'type': 'send.event', 'text': json.dump(text_data)}
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
            plain_text = msg['message'].encode('utf-8')
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
        print('process first-phase finished, phase code %d' % phase)
        (cmd_str, *kargs) = plain_text.split()
        if cmd_str in Handler_dict:
            return_msg = Handler_dict[cmd_str](*kargs)
            await self.send_message(msg_type == 'private', target_id, return_msg)

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
            self.process(msg)

