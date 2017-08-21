from itertools import product
from random import shuffle

from blackjack.moves import double_moves, ace_moves, classic_moves


class Card:
    def __init__(self, token):
        self.token = str(token)

    @property
    def value(self):
        if self.token in ['K', 'Q', 'J']:
            return 10
        elif self.token == 'A':
            return 'A'
        else:
            return int(self.token)

    def __repr__(self):
        return '[{}]'.format(self.token)


class Deck:
    def __init__(self, nb_sabot=6):
        d = [str(c) for c in range(2, 11)]
        d += ['J', 'Q', 'K', 'A']
        d *= nb_sabot * 4
        self.max_cards = nb_sabot * 52
        self.cards = [Card(c) for c in d]
        self.shuffle()

    def draw(self, nb_cards=1, hand=None):
        cards = []
        for i in range(nb_cards):
            card = self.cards.pop(0)
            cards.append(card)
            if hand is not None:
                hand.append(card)
        return tuple(cards)

    def shuffle(self):
        shuffle(self.cards)

    @property
    def nb_cards(self):
        return len(self.cards)


class Hand:
    def __init__(self, *cards):
        if cards is None:
            self.cards = []
        else:
            self.cards = list(cards)

    def append(self, card):
        self.cards.append(card)

    def nb_cards(self):
        return len(self.cards)

    def __repr__(self):
        return ', '.join([str(c) for c in self.cards])

    def too_high(self):
        return min(self.value) > 21

    def split_cards(self):
        if self.is_double():
            other = Hand(self.cards[0])
            self.cards.pop(0)
            return self, other
        return None, None

    @property
    def value(self):
        nb_as = [c.token for c in self.cards].count('A')
        values = set()
        for a_values in product([1, 11], repeat=nb_as):
            cards_values = [c.value for c in self.cards if c.token != 'A']
            values.add(sum(cards_values) + sum(a_values))

        return tuple(sorted(values))

    @property
    def max_valid_value(self):
        valid_values = [value for value in self.value if value <= 21]
        return max(valid_values, default=0)

    def has_ace(self):
        return len([c for c in self.cards if c.value == 'A']) != 0

    def is_double(self):
        return self.nb_cards() == 2 and len({c.value for c in self.cards}) == 1

    def duplicate(self):
        return Hand(self.cards)

    def remove(self, value):
        if not self.has_card(value):
            raise Exception("No such card")
        self.cards = [c for c in self.cards if c.value != value]

    def remove_one(self, value):
        ind = 0
        for i, card in enumerate(self.cards):
            if card.value is value:
                ind = i
                break
        self.cards.pop(ind)

    def has_card(self, value):
        return value in [c.value for c in self.cards]

    def change_extra_aces(self):
        while max(self.value) > 21:
            self.remove_one('A')
            self.append(Card('1'))


def basic_strategy(p_hand: Hand, c_card: Card):
    p_hand = Hand(p_hand.cards)
    if min(p_hand.value) > 21:
        return "L"
    if p_hand.is_double():
        h_value = p_hand.cards[0].value
        return double_moves[h_value][c_card.value]
    p_hand.change_extra_aces()
    if p_hand.has_ace():
        other = Hand(p_hand.cards)
        other.remove('A')
        value = min(other.value)
        return ace_moves[value][c_card.value]
    else:
        value = min(p_hand.value)
        return classic_moves[value][c_card.value]
