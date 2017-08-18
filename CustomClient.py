import sys

from fbchat import Client, ThreadType

from MessageEvent import MessageEvent


class CustomClient(Client):
    def __init__(self):
        email, password = None, None
        if len(sys.argv) >= 3:
            email, password = sys.argv[1], sys.argv[2]
        else:
            exit()
        super(CustomClient, self).__init__(email, password, max_tries=1)
        self.functions = []

    def onMessage(self, mid=None, author_id=None, message=None, thread_id=None, thread_type=ThreadType.USER, ts=None,
                  metadata=None, msg=None):
        if msg is None:
            msg = {}
        m_event = MessageEvent(mid, author_id, message, thread_id, thread_type, ts, metadata, msg)
        for validate in self.functions:
            validate(m_event)

    def set_action(self, validate):
        self.functions.append(validate)
