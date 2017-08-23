from fbchat import MessageReaction

from bot.MessageEvent import MessageEvent

from blackjack.Player import Player
from bot.CustomClient import CustomClient


class MessengerBot:
    def __init__(self, client: CustomClient):
        self.client = client
        self.client.set_action(self.validate)

    def validate(self, m_event: MessageEvent):
        pass

    def answer_back(self, m_event: MessageEvent, message: str):
        self.client.sendMessage(message, thread_id=m_event.thread_id, thread_type=m_event.thread_type)

    def react_tumb_up(self, m_event: MessageEvent):
        self.client.reactToMessage(m_event.mid, MessageReaction.YES)

class MultiCommandBot(MessengerBot):
    def __init__(self, client):
        super(MultiCommandBot, self).__init__(client)

        self.commands = {"/{}".format('_'.join(method.split('_')[1:])): getattr(self, method)
                         for method in dir(self)
                         if callable(getattr(self, method))
                         if method.startswith("on_")}

    def validate(self, m: MessageEvent):
        command, *rest = m.message.split(' ')
        m.message = " ".join(rest)
        command = command.lower()
        if command in self.commands:
            self.commands[command](m)
