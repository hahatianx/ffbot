#coding=utf-8

import socket
from .utils import process, serialize, deserialize


class Cqbot(object):
    def __init__(self,
                 bot_addr,
                 bot_port,
                 is_debug=False,
                 is_online=True,
                 ):
        self.bot_addr_tuple = (bot_addr, bot_port)
        self.srv_addr_tuple = ('localhost', 8888)
        self.is_debug = is_debug
        self.is_online = is_online
        self.send_fd = socket.socket(socket.AF_INET,
                                     socket.SOCK_DGRAM)
        self.lstn_fd = socket.socket(socket.AF_INET,
                                     socket.SOCK_DGRAM)
        self.lstn_fd.bind(self.srv_addr_tuple)
        self.lstn_fd.listen()

    def __del__(self):
        self.send_fd.close()
        self.lstn_fd.close()

    def run(self):
        if not self.online:
            return

        while True:
            msg = deserialize(self.lstn_fd.recvfrom(1024))
            is_success, return_msg = process(msg)
            if is_success:
                self.send_fd.sendto(serialize(return_msg))


if __name__ == '__main__':
    bot = Cqbot('localhost', 8080, True, True)
    try:
        bot.run()
    except KeyboardInterrupt:
        pass
