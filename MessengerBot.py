from CustomClient import CustomClient
from MessageEvent import MessageEvent


class MessengerBot:
    def __init__(self, client: CustomClient):
        self.client = client
        self.client.set_action(self.validate)

    def validate(self, m_event: MessageEvent):
        pass

    def answer_back(self, m_event: MessageEvent, message: str):
        self.client.sendMessage(message, thread_id=m_event.thread_id, thread_type=m_event.thread_type)


class MultiCommandBot(MessengerBot):
    def __init__(self, client):
        super(MultiCommandBot, self).__init__(client)

        self.commands = {"/{}".format('_'.join(method.split('_')[1:])): getattr(self, method)
                         for method in dir(self)
                         if callable(getattr(self, method))
                         if method.startswith("on_")}

    def validate(self, m_event: MessageEvent):
        command = m_event.message.split(' ')[0]
        if command in self.commands:
            self.commands[command](m_event)

    def func(self, m_event: MessageEvent):
        self.commands[m_event.message.split(' ')[0]](m_event)
