from fbchat import MessageReaction

from bot.CustomClient import CustomClient
from bot.MessageEvent import MessageEvent


class MessengerBot:
    def __init__(self, client: CustomClient, threads: list = None):
        self.threads = threads
        self.client = client
        self.client.set_action(self.validate)

    def validate(self, m_event: MessageEvent):
        if self.threads is None or m_event.thread_id in self.threads:
            self.action(m_event)

    def action(self, m_event: MessageEvent):
        pass

    def answer_back(self, m_event: MessageEvent, message: str):
        self.client.sendMessage(message, thread_id=m_event.thread_id, thread_type=m_event.thread_type)

    def react_thumb_up(self, message_id):
        self.client.reactToMessage(message_id, MessageReaction.YES)

    def listen(self):
        self.client.listen()


class MultiCommandBot(MessengerBot):
    def __init__(self, client, threads=None):
        super(MultiCommandBot, self).__init__(client, threads)

        self.commands = {"/{}".format('_'.join(method.split('_')[1:])): getattr(self, method)
                         for method in dir(self)
                         if callable(getattr(self, method))
                         if method.startswith("cmd_")}

    def action(self, m: MessageEvent):
        command, *rest = m.message.split(' ')
        command = command.lower()
        if command in self.commands:
            m.message = " ".join(rest)
            self.commands[command](m)
        else:
            self.any(m)

    def any(self, m: MessageEvent):
        pass
