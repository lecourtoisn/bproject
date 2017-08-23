from threading import Timer

from fbchat import ThreadType

from blackjack.BlackjackTable import BlackjackTable, Phase
from bot.MessageEvent import MessageEvent
from bot.MessengerBot import MultiCommandBot
from data_cache.PCache import PCache

DEBUG_THREAD_ID = "1573965122648233"
# PROD_THREAD_ID = "1573965122648233"
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
    def wrapper(self, m: MessageEvent, *_, **kwargs):
        table = self.table
        player = PCache.get(m.author_id)
        if table.in_game(player):
            func(self, m, *_, **kwargs)

    return wrapper


def has_valid_hand(func):
    def wrapper(self, m: MessageEvent, *_, **kwargs):
        table = self.table
        player = PCache.get(m.author_id)
        if table.has_valid_hands(player):
            func(self, m, *_, **kwargs)

    return wrapper


class BlackjackBot(MultiCommandBot):
    def __init__(self, client):
        super().__init__(client)
        self.casino_thread_id = PROD_THREAD_ID
        self.table = BlackjackTable()
        self.betting_delay = 30.0
        self.actions_delay = 60.0
        self.max_bet = 100

    def send_casino(self, message):
        self.client.sendMessage(message, thread_id=self.casino_thread_id, thread_type=ThreadType.GROUP)

    @on_phase(Phase.BETTING, Phase.NONE)
    def on_bet(self, m: MessageEvent):
        table = self.table
        player = PCache.get(m.author_id)
        if player.name is None:
            player.name = self.client.get_author(m.author_id).name
        bet = abs(int(m.message))
        if bet > self.max_bet:
            return
        if table.phase is Phase.NONE:
            table.set_table()
            self.send_casino(
                "Nouvelle manche de Black jack, faites vos jeux. Mise maximale : {}. Vous avez {} secondes".format(
                    str(self.max_bet), int(self.betting_delay)))

            if m.thread_id != self.casino_thread_id:
                self.answer_back(m, "Nouvelle manche de Black jack, faites vos jeux. Vous avez {} secondes".format(
                    int(self.betting_delay)))
            Timer(self.betting_delay, self.close_bets, [m]).start()
        try:
            self.client.addUsersToGroup([m.author_id], self.casino_thread_id)
        except:
            print("Already in conv")

        table.bet(player, bet)
        self.send_casino("{} a misé {}".format(player.name, bet))

    def close_bets(self, m: MessageEvent):
        table = self.table
        response = ["Les jeux sont faits\n"]
        if m.thread_id != self.casino_thread_id:
            self.answer_back(m, response[0][:-1])
        table.initial_distribution()
        bank_hand = table.bank_hand
        response.append("Première carte de la banque : {} ({})\n".format(str(bank_hand), bank_hand.readable_value))
        for player, hand in table.get_hands():
            response.append("{} : {} ({})".format(player.name, str(hand), hand.max_valid_value))
        response.append("\n/hit pour une nouvelle carte, /stand pour rester, /double pour doubler, /split pour séparer")
        response.append("Vous avez {} secondes".format(int(self.actions_delay)))
        self.send_casino("\n".join(response))

        Timer(self.actions_delay, self.bank_turn, [table.game_id]).start()

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_hit(self, m: MessageEvent):
        table = self.table
        player = PCache.get(m.author_id)
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
            self.bank_turn()

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

    @on_phase(Phase.ACTIONS)
    def bank_turn(self, game_id):
        table = self.table
        if table.game_id != game_id:
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
        response = ["[Blackjack scores]"]

        for place, (name, score) in enumerate(scores[lower_bound:higher_bound]):
            response.append("#{} {}: {}".format(place + 1, name, score))

        self.answer_back(m, "\n".join(response))
