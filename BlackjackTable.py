from enum import Enum
from typing import List, Dict, Tuple

from Player import Player
from blackjack.game import Hand, Deck


class Phase(Enum):
    BETTING = 1
    NONE = 2
    ACTIONS = 3


class HandContext:
    def __init__(self, hand):
        self.hand = hand
        self.doubled = False
        self.is_split = False
        self.stood = False

    def min_value(self):
        return min(self.hand.value)

    def is_invalid(self):
        return self.min_value() > 21 or self.stood

    def resolve(self, dealer_hand: Hand, bet) -> Tuple[bool, int]:
        dealer_bj = dealer_hand.max_valid_value == 21 and len(dealer_hand.cards) == 2
        player_bj = self.hand.max_valid_value == 21 and len(self.hand.cards) == 2 and not self.is_split
        if dealer_bj and player_bj:
            return None, 0
        real_bet = bet * 2 if self.doubled else bet
        if dealer_bj and not player_bj:
            return False, -1 * real_bet
        if not dealer_bj and player_bj:
            return True, int(real_bet * 1.5)

        if self.hand.max_valid_value > dealer_hand.max_valid_value:
            return True, real_bet
        elif self.hand.max_valid_value == 0 or dealer_hand.max_valid_value > self.hand.max_valid_value:
            return False, -1 * real_bet
        else:
            return None, 0


class PlayerContext:
    def __init__(self, player, bet):
        self.player = player
        self.bet = bet
        self._hand_contexts = []

    @property
    def hand_contexts(self) -> List[HandContext]:
        return self._hand_contexts

    def get_valid_hand_contexts(self) -> List[HandContext]:
        return [h_ctx for h_ctx in self.hand_contexts if not h_ctx.is_invalid()]

    def has_valid_hands(self):
        return len(self.get_valid_hand_contexts()) > 0


class BlackjackTable:
    def __init__(self):
        self.phase = Phase.NONE
        self.bank_hand = Hand()
        self._player_contexts = {}
        self.deck = Deck()

    @property
    def player_contexts(self) -> Dict[Player, PlayerContext]:
        return self._player_contexts

    def set_table(self):
        if self.deck.nb_cards < 30:
            self.deck = Deck()
        self.bank_hand = Hand()
        self._player_contexts = {}
        self.phase = Phase.BETTING

    def bet(self, player: Player, bet):
        self.player_contexts[player] = PlayerContext(player, bet)

    def initial_distribution(self):
        for player_context in self.player_contexts.values():
            hand = Hand()
            self.deck.draw(2, hand)
            player_context.hand_contexts.append(HandContext(hand))
        self.bank_hand = Hand()
        self.deck.draw(1, self.bank_hand)
        self.phase = Phase.ACTIONS

    def distribute_bank(self):
        while min(self.bank_hand.value) < 17:
            self.deck.draw(1, self.bank_hand)

    def hit(self, player: Player) -> Hand:
        p_ctx = self.player_contexts[player]
        hand_ctxs = p_ctx.get_valid_hand_contexts()
        hand = None
        if len(hand_ctxs) != 0:
            hand = hand_ctxs[0].hand
            self.deck.draw(1, hand)
        return hand

    def stand(self, player: Player) -> Hand:
        p_ctx = self.player_contexts[player]
        hand_ctxs = p_ctx.get_valid_hand_contexts()
        hand = None
        if len(hand_ctxs) != 0:
            hand = hand_ctxs[0].hand
            hand_ctxs[0].stood = True
        return hand

    def split_cards(self, player: Player) -> Tuple[Hand, Hand]:
        p_ctx = self.player_contexts[player]
        hand_ctxs = p_ctx.get_valid_hand_contexts()
        if len(hand_ctxs) != 0:
            hand = hand_ctxs[0].hand
            if hand.is_double():
                hand, new_hand = hand.split_cards()
                new_ctx = HandContext(new_hand)
                hand_ctxs[0].is_split = True
                new_ctx.is_split = True
                p_ctx.hand_contexts.append(new_ctx)
                return hand, new_hand
        return hand, hand

    def double(self, player: Player) -> Hand:
        p_ctx = self.player_contexts[player]
        hand_ctxs = p_ctx.get_valid_hand_contexts()
        hand = None
        if len(hand_ctxs) != 0:
            hand_ctxs[0].doubled = True
            hand_ctxs[0].stood = True
            hand = hand_ctxs[0].hand
            self.deck.draw(1, hand)
        return hand

    def reward(self):
        self.phase = Phase.NONE

    def get_hands(self):
        return [(p, h_ctx.hand) for p, p_ctx in self.player_contexts.items() for h_ctx in p_ctx.hand_contexts]

    def in_game(self, player: Player) -> bool:
        return player in self.player_contexts

    def has_valid_hands(self, player: Player) -> bool:
        p_ctx = self.player_contexts[player]
        return p_ctx.has_valid_hands()

    def dealing_is_over(self):
        return not any([h.has_valid_hands() for h in self.player_contexts.values()])

    def bank_busted(self):
        return self.bank_hand.too_high()

    def summary(self):
        summary = []
        for p, p_ctx in self.player_contexts.items():
            for h_ctx in p_ctx.hand_contexts:
                summary.append((p, h_ctx.hand, *h_ctx.resolve(self.bank_hand, p_ctx.bet)))

        return summary
