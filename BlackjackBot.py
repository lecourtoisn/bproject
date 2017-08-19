from collections import defaultdict
from enum import Enum
from threading import Timer

from MessageEvent import MessageEvent
from MessengerBot import MultiCommandBot
from blackjack.game import Deck, Hand


class Phase(Enum):
    BETTING = 1
    NONE = 2
    ACTIONS = 3


def on_phase(*phases: list):
    def decorator(func):
        def wrapper(self, m_event: MessageEvent, *_, **kwargs):
            phase = self.phases[m_event.thread_id]
            if phase in phases:
                func(self, m_event, *_, **kwargs)

        return wrapper

    return decorator


class BlackjackBot(MultiCommandBot):
    def __init__(self, client):
        super().__init__(client)
        self.phases = defaultdict(lambda: Phase.NONE)
        self.bets = defaultdict(dict)
        self.hands = defaultdict(lambda: defaultdict(lambda: Hand()))
        self.banks = defaultdict(lambda: Hand())
        self.deck = Deck()
        self.betting_delay = 5.0

    @on_phase(Phase.BETTING, Phase.NONE)
    def on_bet(self, m_event: MessageEvent):
        author_id, thread_id, message = m_event.author_id, m_event.thread_id, m_event.message
        author = self.client.get_author(author_id)
        bet = int(message)
        phase = self.phases[thread_id]
        if phase is Phase.NONE:
            self.phases[thread_id] = Phase.BETTING
            self.answer_back(m_event, "Nouvelle manche de Black jack, fates vos jeux. Vous avez {} secondes".format(
                int(self.betting_delay)))
        self.bets[thread_id][author_id] = bet
        self.answer_back(m_event, "{} a parié {}".format(author.name, message))
        t = Timer(self.betting_delay, self.close_bets, [thread_id, m_event])
        t.start()

    def close_bets(self, thread_id: str, m_event: MessageEvent):
        self.phases[thread_id] = Phase.ACTIONS
        hands = self.hands[thread_id]
        response = ["Les jeux sont faits"]
        for player_id, bet in self.bets[thread_id].items():
            player = self.client.get_author(player_id)
            hand = hands[player_id]
            self.deck.draw(2, hand)
            response.append("{} : {}".format(player.name, str(hand)))
        bank_hand = self.banks[thread_id]
        self.deck.draw(1, bank_hand)
        response.append("")
        response.append("Première carte de la banque : {}".format(str(bank_hand)))
        response.append("")
        response.append("/card pour une nouvelle carte, /stay pour rester, /double pour doubler, /split pour séparer")
        self.answer_back(m_event, "\n".join(response))

    @on_phase(Phase.ACTIONS)
    def on_card(self, m_event: MessageEvent):
        print("ok")
        self.terminate(m_event.thread_id)

    def terminate(self, thread_id: str):
        self.phases.pop(thread_id)
        self.bets.pop(thread_id)
        self.hands.pop(thread_id)
        self.banks.pop(thread_id)
