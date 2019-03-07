#coding=utf-8

import django
from collections import namedtuple
from base64 import b64encode, b64decode
from ffbot.bot.BOT.handlers import EchoHandler

ClientHello = namedtuple("ClientHello", ("port"))
ServerHello = namedtuple("ServerHello", ())

RcvdPrivateMessage = namedtuple("RcvdPrivateMessage", ("qq", "text"))
SendPrivateMessage = namedtuple("SendPrivateMessage", ("qq", "text"))

RcvdGroupMessage = namedtuple("RcvdGroupMessage", ("group", "qq", "text"))
SendGroupMessage = namedtuple("SendGroupMessage", ("group", "text"))

RcvdDiscussMessage = namedtuple("RcvdDiscussMessage",
                                ("discuss", "qq", "text"))
SendDiscussMessage = namedtuple("SendDiscussMessage",
                                ("discuss", "text"))

GroupMemberDecrease = namedtuple("GroupMemberDecrease",
                                 ("group", "qq", "operatedQQ"))
GroupMemberIncrease = namedtuple("GroupMemberIncrease",
                                 ("group", "qq", "operatedQQ"))
GroupBan = namedtuple("GroupBan", ("group", "qq", "duration"))

Fatal = namedtuple("Fatal", ("text"))

FrameType = namedtuple("FrameType", ("prefix", "rcvd", "send"))
FRAME_TYPES = (
    FrameType("ClientHello", (), ClientHello),
    FrameType("ServerHello", ServerHello, ()),
    FrameType("PrivateMessage", RcvdPrivateMessage, SendPrivateMessage),
    FrameType("DiscussMessage", RcvdDiscussMessage, SendDiscussMessage),
    FrameType("GroupMessage", RcvdGroupMessage, SendGroupMessage),
    FrameType("GroupMemberDecrease", GroupMemberDecrease, ()),
    FrameType("GroupMemberIncrease", GroupMemberIncrease, ()),
    FrameType("GroupBan", (), GroupBan),
    FrameType("Fatal", (), Fatal),
)


def serialize(data):
    if isinstance(data, str):
        parts = data.split()
    elif isinstance(data, list):
        parts = data
    else:
        raise TypeError()

    (prefix, *payload) = parts
    for type_ in FRAME_TYPES:
        if prefix == type_.prefix:
            frame = type_.rcvd(*payload)
    # decode text
    if isinstance(frame, (
            RcvdPrivateMessage, RcvdGroupMessage, RcvdDiscussMessage)):
        payload[-1] = b64decode(payload[-1]).decode('gbk')
        frame = type(frame)(*payload)
    return frame


def deserialize(frame):
    if not isinstance(frame, (tuple, list)):
        raise TypeError()

    # Cast all payload fields to string
    payload = list(map(lambda x: str(x), frame))

    # encode text
    if isinstance(frame, (
            SendPrivateMessage, SendGroupMessage, SendDiscussMessage, Fatal)):
        payload[-1] = b64encode(payload[-1].encode('gbk')).decode()

    for type_ in FRAME_TYPES:
        if isinstance(frame, type_.send):
            data = ' '.join((type_.prefix, *payload))
    return data


def handle_raw_data(data):
    (msg_type, *others) = data.split()



handler_dict = {
    '/echo': EchoHandler,
}
# process every msg, ignore if without leading slash('/')
# return values,   if_success, return_msg
def process(msg, debug):
    (cmd, *kargs) = msg.split()
    is_success, return_msg = False, ''
    if debug:
        print(cmd, *kargs)
    for cmd_pattern, cmd_handler in handler_dict:
        if cmd_pattern == cmd.strip():
            is_success = True
            return_msg = cmd_handler(*kargs)
            break
    return is_success, return_msg




