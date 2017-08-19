import MessageEvent
from MessengerBot import MultiCommandBot


class BlackjackBot(MultiCommandBot):
    def on_draw(self, m_event: MessageEvent):
        print("in on draw", m_event.message)

    def on_double(self, m_event: MessageEvent):
        print("in double cards", m_event.message)
