from enum import Enum

import Player
from blackjack.game import Hand, Deck


class Phase(Enum):
    BETTING = 1
    NONE = 2
    ACTIONS = 3


class BlackjackTable:
    def __init__(self):
        self.phase = Phase.NONE
        self.bank_hand = Hand()
        self.player_contexts = []
        self.deck = Deck()

    def set_table(self):
        if self.deck.nb_cards < 30:
            self.deck = Deck()
        self.bank_hand = Hand()
        self.player_contexts = {}
        self.phase = Phase.BETTING

    def bet(self, player: Player, amount):
        pass

    def initial_distribution(self):
        pass

    def distribute_bank(self):
        pass

    def hit_player(self, player: Player) -> Hand:
        pass

    def stand_player(self, player: Player) -> Hand:
        pass

    def split(self):
        pass

    def double(self):
        pass

    def reward(self):
        self.phase = Phase.NONE

    def get_hands(self):
        pass

    def in_game(self, player: Player) -> bool:
        pass

    def did_not_stood(self, player: Player) -> bool:
        pass

    def dealing_is_over(self):
        pass

    def bank_busted(self):
        pass

    def summary(self):
        pass


class PlayerContext:
    def __init__(self, player):
        self.player = player
        self.hands = []


class HandContext:
    def __init__(self, bet, hand):
        self.bet = bet
        self.hand = hand
        self.doubled = False
        self.is_split = False
