from threading import Timer

import emoji
from fbchat import ThreadType

from blackjack.BlackjackTable import BlackjackTable, Phase
from blackjack.Player import Player
from bot.MessageEvent import MessageEvent
from bot.MessengerBot import MultiCommandBot
from data_cache.PCache import PCache

DEBUG_THREAD_ID = "1573965122648233"
PROD_THREAD_ID = "1526063594106602"


#
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


class Observers(object):
    def new_round(self, shuffled=False):
        pass

    def cards_distributed(self, bank_hand, players_hands):
        pass


class BlackjackEngine:
    def __init__(self, client):
        super().__init__(client)
        self.table = BlackjackTable()
        self.betting_delay = 15.0
        self.actions_delay = 60.0
        self.max_bet = 100

        self.observers = []

    @on_phase(Phase.BETTING, Phase.NONE)
    def bet(self, player_id, amount: int):
        table = self.table
        bet = abs(amount)
        if bet > self.max_bet:
            return
        if table.phase is Phase.NONE:
            shuffled = table.set_table()
            for o in self.observers:
                o.new_round(shuffled=shuffled)

            Timer(self.betting_delay, self.close_bets).start()

        player = PCache.get(player_id)
        table.bet(player, bet)

    def close_bets(self):
        table = self.table
        table.initial_distribution()
        bank_hand = table.bank_hand
        for o in self.observers:
            o.cards_distributed(bank_hand=bank_hand, players_hands=table.get_hands())

        Timer(self.actions_delay, self.bank_turn, [table.game_id]).start()

        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_hit(self, player_id):
        table = self.table
        player = PCache.get(player_id)
        hand = table.hit(player)
        self.send_casino("{} : {} ({})".format(player.name, str(hand), hand.readable_value))

        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_stand(self, m: MessageEvent):
        table = self.table
        player = PCache.get(m.author_id)
        table.stand(player)

        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_double(self, m: MessageEvent):
        table = self.table
        player = PCache.get(m.author_id)
        hand = table.double(player)
        self.send_casino("{} : {} ({})".format(player.name, str(hand), hand.readable_value))

        if table.dealing_is_over():
            self.bank_turn(table.game_id)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_split(self, m: MessageEvent):
        table = self.table
        player = PCache.get(m.author_id)
        hand, other_hand = table.split_cards(player)
        if hand is not None and other_hand is not None:
            self.send_casino("{} : {} ({})".format(player.name, str(hand), hand.readable_value))
            self.send_casino("{} : {} ({})".format(player.name, str(other_hand), other_hand.readable_value))

    def bank_turn(self, game_id):
        table = self.table
        if table.phase != Phase.ACTIONS or table.game_id != game_id:
            return
        table.distribute_bank()
        table.reward()
        bank_hand = table.bank_hand
        response = ["Cartes de la banque: {} ({})\n".format(str(bank_hand), bank_hand.readable_value)]
        if table.bank_busted():
            response.append("💀 La banque a sauté, tous les joueurs encore en jeux sont gagnants\n")
        else:
            response.append("La banque marque {} points".format(bank_hand.max_valid_value))

        for player, hand, win, bet in table.summary():
            if win is True:
                ending_str = "Gain de {} 💲".format(bet)
            elif win is False:
                ending_str = "Perte de {} 💀".format(abs(bet))
            else:
                ending_str = "Egalité, aucun gain, aucune perte"
            recap_str = "{} : {} ({}) => {}".format(player.name, str(hand), hand.readable_value, ending_str)
            response.append(recap_str)
        self.send_casino("\n".join(response))

    def on_debug(self, _: MessageEvent):
        self.betting_delay = 5.0
        self.actions_delay = 5.0
        self.casino_thread_id = DEBUG_THREAD_ID

    def on_prod(self, _: MessageEvent):
        self.betting_delay = 30.0
        self.actions_delay = 60.0
        self.casino_thread_id = PROD_THREAD_ID

    def on_scores(self, m: MessageEvent):
        response = ["[Blackjack scores]"]
        scores = [(p.name, p.cash) for p in PCache.cache.values()]
        scores = sorted(scores, key=lambda s: s[1], reverse=True)
        for place, (name, score) in enumerate(scores[:10]):
            response.append("#{} {}: {}".format(place + 1, name, score))

        self.answer_back(m, "\n".join(response))

    def on_score(self, m: MessageEvent):
        player = PCache.get(m.author_id)
        scores = [(p.name, p.cash) for p in PCache.cache.values()]
        scores = sorted(scores, key=lambda s: s[1], reverse=True)
        p_place = scores.index((player.name, player.cash))
        lower_bound = p_place - 2
        lower_bound = 0 if lower_bound < 0 else lower_bound
        higher_bound = lower_bound + 5
        response = ["[Blackjack personal score]"]

        for place, (name, score) in enumerate(scores[lower_bound:higher_bound]):
            response.append("#{} {}: {}".format(place + 1 + lower_bound, name, score))

        self.answer_back(m, "\n".join(response))

    def on_help(self, m: MessageEvent):
        message = ["[Règles du Blackjack",
                   "Le but du Blackjack est de tirer des cartes jusqu'à approcher le plus possible de 21 sans le dépasser",
                   "Le joueur gagne si sa main à plus de valeur que celle de a banque et qu'il n'a pas dépassé 21",
                   "La banque tire en dessous de 17 et reste à 17 ou plus",
                   "",
                   "Les cartes de 2 à 10 valent autant de point", "Les têtes valent 10 points",
                   "L'as vaut 1 ou 11 points à l'avantage du joueur",
                   "",
                   "Un as plus une tête est un Blackjack, et vous rapportera 1,5 fois votre mise en cas de victoire",
                   "Toute combinaison de 3 carte ou plus, même si elle vaut 21 points, a moins de valeur qu'un Blackjack",
                   "",
                   "/hit: demande une carte suplémentaire",
                   "/double: double sa mise et demande une dernière carte",
                   "/split: si vous avez une paire, split sépare votre paire en deux jeux indépendants",
                   "/stand: signale que vous ne souhaitez plus de carte"]
        self.client.sendMessage('\n'.join(message), m.author_id)
