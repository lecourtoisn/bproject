import inspect
from optparse import OptionParser
from pprint import pprint

from MessageEvent import MessageEvent
from CustomClient import CustomClient


class MessengerBot:
    def __init__(self, client: CustomClient):
        self.client = client
        self.client.set_action(self.validate, self.func)

    def validate(self, m_event: MessageEvent):
        pass

    def func(self, m_event: MessageEvent):
        pass

    def answer_back(self, m_event: MessageEvent, message: str):
        self.client.sendMessage(message, thread_id=m_event.thread_id, thread_type=m_event.thread_type)


class CommandBot(MessengerBot):
    def __init__(self, client: CustomClient, command: str):
        super(CommandBot, self).__init__(client)
        self.command = command

    def validate(self, m_event: MessageEvent):
        if m_event.message.lower().startswith(self.command):
            m_event.message = ' '.join(m_event.message.split(' ')[1:])
            return True
        return False


class MultiCommandBot:
    def __init__(self):
        pass
        # a = inspect.getmembers(OptionParser, predicate=inspect.ismethod)

    def on_draw(self, m_event: MessageEvent):

        # pprint([method for method in inspect.getmembers(self)][-1])
        a = inspect.getmembers(self)[-1]
        print(inspect.ismethod(a))
        # print([method for method in inspect.getmembers(self) if inspect.ismethod(method)])
        # print(inspect.getmembers(OptionParser, predicate=inspect.ismethod))


class Blackjack(CommandBot):
    def __init__(self, client):
        super(Blackjack, self).__init__(client, "/draw")

    def func(self, m_event: MessageEvent):
        self.answer_back(m_event, m_event.message)
