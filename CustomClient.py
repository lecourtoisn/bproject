import json

from fbchat import Client, ThreadType

from MessageEvent import MessageEvent


class CustomClient(Client):
    def __init__(self, email, password, session=None):
        super(CustomClient, self).__init__(email, password, max_tries=1, session_cookies=session)
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

    def onLoggedIn(self, email=None):
        with open("session.txt", "w") as file:
            json.dump(self.getSession(), file)

    def get_author(self, author_id: str) -> dict:
        user = self.fetchUserInfo(author_id)[author_id]
        return user
