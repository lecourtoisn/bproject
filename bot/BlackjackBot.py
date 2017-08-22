from collections import defaultdict
from threading import Timer

from fbchat import ThreadType

from bot.MessengerBot import MultiCommandBot

from blackjack.BlackjackTable import BlackjackTable, Phase
from bot.MessageEvent import MessageEvent


def on_phase(*phases: list):
    def decorator(func):
        def wrapper(self, m: MessageEvent, *_, **kwargs):
            table = self.table
            if table.phase in phases:
                func(self, m, *_, **kwargs)

        return wrapper

    return decorator


def playing(func):
    def wrapper(self, m: MessageEvent, *_, **kwargs):
        table = self.table
        if table.in_game(m.player):
            func(self, m, *_, **kwargs)

    return wrapper


def has_valid_hand(func):
    def wrapper(self, m: MessageEvent, *_, **kwargs):
        table = self.table
        if table.has_valid_hands(m.player):
            func(self, m, *_, **kwargs)

    return wrapper


class BlackjackBot(MultiCommandBot):
    def __init__(self, client):
        super().__init__(client)
        self.casino_thread_id = "1573965122648233"
        self.table = BlackjackTable()
        self.betting_delay = 30.0
        self.actions_delay = 60.0

    def send_casino(self, message):
        self.client.sendMessage(message, thread_id=self.casino_thread_id, thread_type=ThreadType.GROUP)

    @on_phase(Phase.BETTING, Phase.NONE)
    def on_bet(self, m: MessageEvent):
        table = self.table
        bet = abs(int(m.message))
        if table.phase is Phase.NONE:
            table.set_table()
            self.answer_back(m, "Nouvelle manche de Black jack, faites vos jeux. Vous avez {} secondes".format(
                int(self.betting_delay)))
            self.send_casino("Nouvelle manche de Black jack, faites vos jeux. Vous avez {} secondes".format(
                int(self.betting_delay)))
            Timer(self.betting_delay, self.close_bets).start()
        try:
            self.client.addUsersToGroup([m.author_id], self.casino_thread_id)
        except:
            print("Already in conv")

        table.bet(m.player, bet)
        self.send_casino("{} a misé {}".format(m.author.name, bet))

    def close_bets(self):
        table = self.table
        response = ["Les jeux sont faits\n"]
        table.initial_distribution()
        bank_hand = table.bank_hand
        response.append("Première carte de la banque : {} ({})\n".format(str(bank_hand), bank_hand.readable_value))
        for player, hand in table.get_hands():
            response.append("{} : {} ({})".format(player.name, str(hand), hand.max_valid_value))
        response.append("\n/hit pour une nouvelle carte, /stand pour rester, /double pour doubler, /split pour séparer")
        self.send_casino("\n".join(response))

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_hit(self, m: MessageEvent):
        table = self.table
        hand = table.hit(m.player)
        self.send_casino("{} : {} ({})".format(m.player.name, str(hand), hand.readable_value))

        if table.dealing_is_over():
            self.bank_turn()

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_stand(self, m: MessageEvent):
        table = self.table
        table.stand(m.player)

        if table.dealing_is_over():
            self.bank_turn()

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_double(self, m: MessageEvent):
        table = self.table
        hand = table.double(m.player)
        self.send_casino("{} : {} ({})".format(m.player.name, str(hand), hand.readable_value))

        if table.dealing_is_over():
            self.bank_turn()

    @on_phase(Phase.ACTIONS)
    @has_valid_hand
    @playing
    def on_split(self, m: MessageEvent):
        table = self.table
        hand, other_hand = table.split_cards(m.player)
        if hand is not None and other_hand is not None:
            self.send_casino("{} : {} ({})".format(m.player.name, str(hand), hand.readable_value))
            self.send_casino("{} : {} ({})".format(m.player.name, str(other_hand), other_hand.readable_value))

    def bank_turn(self):
        table = self.table
        table.distribute_bank()
        table.reward()
        bank_hand = table.bank_hand
        response = ["Cartes de la banque: {} ({})\n".format(str(bank_hand), bank_hand.readable_value)]
        if table.bank_busted():
            response.append("La banque a sauté, tous les joueurs encore en jeux sont gagnants\n")
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
