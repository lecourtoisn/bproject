from fbchat import ThreadType


class MessageEvent:
    def __init__(self, mid=None, author_id=None, message=None, thread_id=None, thread_type=ThreadType.USER, ts=None,
                 metadata=None, msg=None):
        self.mid = mid
        self.author_id = author_id
        self.message = message
        self.thread_id = thread_id
        self.thread_type = thread_type
        self.ts = ts
        self.metadata = metadata
        self.msg = msg
        self.player = None
        self.author = None
