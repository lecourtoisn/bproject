from collections import defaultdict
from threading import Timer

from bot.MessengerBot import MultiCommandBot

from blackjack.BlackjackTable import BlackjackTable, Phase
from bot.MessageEvent import MessageEvent


def on_phase(*phases: list):
    def decorator(func):
        def wrapper(self, m: MessageEvent, *_, **kwargs):
            table = self.tables[m.thread_id]
            if table.phase in phases:
                func(self, m, *_, **kwargs)

        return wrapper

    return decorator


def playing(func):
    def wrapper(self, m: MessageEvent, *_, **kwargs):
        table = self.tables[m.thread_id]
        if table.in_game(m.player):
            func(self, m, *_, **kwargs)

    return wrapper


def has_valid_hand(func):
    def wrapper(self, m: MessageEvent, *_, **kwargs):
        table = self.tables[m.thread_id]
        if table.has_valid_hands(m.player):
            func(self, m, *_, **kwargs)

    return wrapper


class BlackjackBot(MultiCommandBot):
    def __init__(self, client):
        super().__init__(client)
        self.tables = defaultdict(lambda: BlackjackTable())
        self.betting_delay = 5.0

    @on_phase(Phase.BETTING, Phase.NONE)
    def on_bet(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        bet = abs(int(m.message))
        if table.phase is Phase.NONE:
            table.set_table()
            self.answer_back(m, "Nouvelle manche de Black jack, faites vos jeux. Vous avez {} secondes".format(
                int(self.betting_delay)))
            Timer(self.betting_delay, self.close_bets, [m]).start()
        table.bet(m.player, bet)
        self.answer_back(m, "{} a parié {}".format(m.author.name, bet))

    def close_bets(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        response = ["Les jeux sont faits"]
        table.initial_distribution()
        bank_hand = table.bank_hand
        response.append("\nPremière carte de la banque : {} ({})".format(str(bank_hand), bank_hand.readable_value))
        for player, hand in table.get_hands():
            response.append("{} : {} ({})".format(player.name, str(hand), hand.max_valid_value))
        response.append("\n/hit pour une nouvelle carte, /stand pour rester, /double pour doubler, /split pour séparer")
        self.answer_back(m, "\n".join(response))

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_hit(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        hand = table.hit(m.player)
        self.answer_back(m, "{} : {} ({})".format(m.player.name, str(hand), hand.readable_value))

        if table.dealing_is_over():
            self.bank_turn(m)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_stand(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        table.stand(m.player)

        if table.dealing_is_over():
            self.bank_turn(m)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_double(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        hand = table.double(m.player)
        self.answer_back(m, "{} : {} ({})".format(m.player.name, str(hand), hand.readable_value))

        if table.dealing_is_over():
            self.bank_turn(m)

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_split(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        hand, other_hand = table.split_cards(m.player)
        self.answer_back(m, "{} : {} ({})".format(m.player.name, str(hand), hand.readable_value))
        self.answer_back(m, "{} : {} ({})".format(m.player.name, str(other_hand), other_hand.readable_value))

    def bank_turn(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        table.distribute_bank()
        table.reward()
        bank_hand = table.bank_hand
        response = ["Main de la banque: {} ({})".format(str(bank_hand), bank_hand.readable_value)]
        if table.bank_busted():
            response.append("La banque a sauté, tous les joueurs encore en jeux sont gagnants")
        else:
            response.append("La banque marque {} points".format(bank_hand.max_valid_value))

        for player, hand, win, bet in table.summary():
            result = "{} : {} ({}) => ".format(player.name, str(hand), hand.readable_value)
            if win is True:
                result += "Gain de {}".format(bet)
            elif win is False:
                result += "Perte de {}".format(abs(bet))
            else:
                result += "Egalité, aucun gain, aucune perte"
            response.append(result)
        self.answer_back(m, "\n".join(response))
