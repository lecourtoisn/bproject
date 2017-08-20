from collections import defaultdict
from threading import Timer

from BlackjackTable import BlackjackTable, Phase
from MessageEvent import MessageEvent
from MessengerBot import MultiCommandBot


# Todo: make a deck per thread_id


def on_phase(*phases: list):
    def decorator(func):
        def wrapper(self: BlackjackBot, m: MessageEvent, *_, **kwargs):
            table = self.tables[m.thread_id]
            if table.phase in phases:
                func(self, m, *_, **kwargs)

        return wrapper

    return decorator


def playing(func):
    def wrapper(self: BlackjackBot, m: MessageEvent, *_, **kwargs):
        table = self.tables[m.thread_id]
        if table.in_game(m.player):
            func(self, m, *_, **kwargs)

    return wrapper


def did_not_stood(func):
    def wrapper(self: BlackjackBot, m: MessageEvent, *_, **kwargs):
        table = self.tables[m.thread_id]
        if table.did_not_stood(m.player):
            func(self, m, *_, **kwargs)

    return wrapper


class BlackjackBot(MultiCommandBot):
    def __init__(self, client):
        super().__init__(client)
        self.tables = defaultdict(lambda: BlackjackTable())
        self.betting_delay = 15.0

    @on_phase(Phase.BETTING, Phase.NONE)
    def on_bet(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        bet = int(m.message)
        if table.phase is Phase.NONE:
            table.set_table()
            self.answer_back(m, "Nouvelle manche de Black jack, fates vos jeux. Vous avez {} secondes".format(
                int(self.betting_delay)))
            Timer(self.betting_delay, self.close_bets, [m]).start()
        table.bet(m.player, bet)
        self.answer_back(m, "{} a parié {}".format(m.author.name, m.message))

    def close_bets(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        response = ["Les jeux sont faits"]
        table.initial_distribution()
        table.distribute_bank()
        for player, hand in table.get_hands().items():
            response.append("{} : {}({})".format(player.name, str(hand), hand.value))
        bank_hand = table.bank_hand
        response.append("\nPremière carte de la banque : {}({})".format(str(bank_hand), bank_hand.value))
        response.append("\n/hit pour une nouvelle carte, /stand pour rester, /double pour doubler, /split pour séparer")
        self.answer_back(m, "\n".join(response))

    @on_phase(Phase.ACTIONS)
    @did_not_stood
    @playing
    def on_hit(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        hand = table.hit_player(m.player)
        self.answer_back(m, "{} : {} ({})".format(m.player.name, str(hand), hand.value))

        if table.dealing_is_over():
            self.bank_turn()

    @on_phase(Phase.ACTIONS)
    @did_not_stood
    @playing
    def on_stand(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        table.stand_player(m.player)

        if table.dealing_is_over():
            self.bank_turn()

    def bank_turn(self, m: MessageEvent):
        table = self.tables[m.thread_id]
        table.distribute_bank()
        table.reward()
        bank_hand = table.bank_hand
        response = ["Main de la banque: {}({})".format(str(bank_hand), bank_hand.value)]
        if table.bank_busted():
            response.append("La banque a sauté, tous les joueurs encore en jeux sont gagnants")
        else:
            response.append("La banque marque {} points")

        for player, hand, win, bet in table.summary():
            result = "{} : {}({}) => ".format(player.name, str(hand), hand.value)
            if win is True:
                result += "Gain de {}".format(bet)
            elif win is False:
                result += "Perte de {}".format(bet)
            else:
                result += "Egalité, aucun gain, aucune perte"
