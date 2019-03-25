#coding=utf-8

import time
from bot.consumer import this_heartbeat


if __name__ == '__main__':
    while True:
        this_heartbeat.heartbeat()
        time.sleep(this_heartbeat.time_out)