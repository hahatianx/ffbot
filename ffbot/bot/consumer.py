#coding=utf-8


from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.exceptions import StopConsumer
import json
import pytz
import re
import os
import pymysql
import datetime
import gc
import traceback


class WSConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self):
        gc.collect()
        await self.close()

    # serialize msg to fit <http api for coolq>
    def serialize(self, action, params, echo=None):
        text_data = {
            'action': action,
            'params': params,
        }
        if echo:
            text_data['echo'] = echo
        event = {'text': json.dump(text_data)}
        return event

    # sending msg
    async def send_msg(self, event):
        await self.send(event['text'])

    # 1) deserialize msg  2) handle msg 3) serialize msg 4) send
    async def receive(self, text_data):
        msg = json.loads(text_data)
        try:
            self.post_type = msg['post_type']
            self.msg_type = msg['message_type']
            self.message = msg['message']
        except:
            traceback.print_exc()
        if 'message' in msg.keys() and self.msg_type == 'private':
            print(self.message)


