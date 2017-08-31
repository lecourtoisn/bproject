from threading import Timer

from blackjack.BlackjackTable import BlackjackTable, Phase
from blackjack.game import Hand
from data_cache.PCache import PCache

DEBUG_THREAD_ID = "1573965122648233"
PROD_THREAD_ID = "1526063594106602"


def on_phase(*phases: list):
    def decorator(func):
        def wrapper(self, *_, **kwargs):
            table = self.table
            if table.phase in phases:
                func(self, *_, **kwargs)

        return wrapper

    return decorator


def playing(func):
    def wrapper(self, player_id, *_, **kwargs):
        table = self.table
        player = PCache.get(player_id)
        if table.in_game(player):
            func(self, player_id, *_, **kwargs)

    return wrapper


def has_valid_hand(func):
    def wrapper(self, player_id, *_, **kwargs):
        table = self.table
        player = PCache.get(player_id)
        if table.has_valid_hands(player):
            func(self, player_id, *_, **kwargs)

    return wrapper


class EngineObserver(object):
    def o_new_round(self):
        pass

    def o_bet(self, player_id):
        pass

    def o_cards_distributed(self):
        pass

    def o_hit(self, player_id, hand: Hand):
        pass

    def o_stand(self, player_id):
        pass

    def o_double(self, player_id, hand: Hand):
        pass

    def o_split(self, player_id, hand: Hand, other_hand: Hand):
        pass

    def o_end_round(self):
        pass


class BlackjackEngine:
    def __init__(self):
        self.table = BlackjackTable()
        self.betting_delay = 1.0
        self.actions_delay = 5.0
        self.max_bet = 100
        self.observers = set()

    @on_phase(Phase.BETTING, Phase.NONE)
    def bet(self, player_id, amount: int):
        table = self.table
        bet = abs(amount)
        player = PCache.get(player_id)
        if bet > self.max_bet:
            return  # todo throw exception
        new_round = table.phase is Phase.NONE
        if new_round:
            table.set_table()
            Timer(self.betting_delay, self.close_bets).start()
        table.bet(player, bet)
        if new_round:
            for o in self.observers:
                o.o_new_round()
        for o in self.observers:
            o.o_bet(player_id)

    def close_bets(self):
        table = self.table
        table.initial_distribution()
        for o in self.observers:
            o.o_cards_distributed()

        Timer(self.actions_delay, self.bank_turn, [table.game_id]).start()

        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def hit(self, player_id):
        table = self.table
        player = PCache.get(player_id)
        hand = table.hit(player)
        for o in self.observers:
            o.o_hit(player_id, hand)
        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def stand(self, player_id):
        table = self.table
        player = PCache.get(player_id)
        table.stand(player)

        for o in self.observers:
            o.o_stand(player_id)
        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def double(self, player_id):
        table = self.table
        player = PCache.get(player_id)
        hand = table.double(player)

        for o in self.observers:
            o.o_double(player_id, hand)
        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def split(self, player_id):
        table = self.table
        player = PCache.get(player_id)
        hand, other_hand = table.split_cards(player)
        if hand is not None and other_hand is not None:
            for o in self.observers:
                o.o_split(player_id, hand, other_hand)

    def bank_turn(self, game_id):
        table = self.table
        if table.phase != Phase.ACTIONS or table.game_id != game_id:  # todo change gameid to be in engine
            return
        table.distribute_bank()
        table.reward()

        for o in self.observers:
            o.o_end_round()
