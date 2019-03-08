#coding=utf-8


from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
import gc
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)

LOGGER = logging.getLogger(__name__)

class WSConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self):
        gc.collect()
        await self.close()

    # serialize msg to fit <http api for coolq>
    def serialize(self, action, params):
        text_data = {
            'action': action,
            'params': params,
        }
        event = {'text': json.dump(text_data)}
        return event

    # sending msg
    async def send_msg(self, event):
        await self.send(event['text'])

    def process(self, msg):
        plain_text = msg['message'].encode('utf-8')
        print(plain_text)

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

