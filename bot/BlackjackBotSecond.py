import emoji
from fbchat import ThreadType

from bot.BlackjackEngine import BlackjackEngine, EngineObserver
from bot.MessageEvent import MessageEvent
from bot.MessengerBot import MultiCommandBot
from data_cache.PCache import PCache

DEBUG_THREAD_ID = "1573965122648233"
PROD_THREAD_ID = "367920366739208"


# PROD_THREAD_ID = "1526063594106602"

class BlackjackBotSecond(MultiCommandBot, EngineObserver):
    def __init__(self, client, blackjack_engine: BlackjackEngine):
        super().__init__(client)
        self.casino_thread_id = PROD_THREAD_ID
        self.last_bet_message_id = {}
        self.engine = blackjack_engine
        self.engine.observers.add(self)

    def send_casino(self, message):
        self.client.sendMessage(message, thread_id=self.casino_thread_id, thread_type=ThreadType.GROUP)

    def any(self, m: MessageEvent):
        if m.thread_id == self.casino_thread_id and m.message == emoji.emojize(":money_with_wings:"):
            m.message = "100"
            self.on_bet(m)

    def on_bet(self, m: MessageEvent):
        bet = int(m.message)
        player = PCache.get(m.author_id)
        if player.name is None:
            player.name = self.client.get_author(m.author_id).name

        self.last_bet_message_id[m.author_id] = m.mid
        self.engine.bet(m.author_id, bet)

    def o_new_round(self):
        table = self.engine.table
        self.send_casino(
            "Nouvelle manche de Black jack, faites vos jeux. Mise maximale : {}. Vous avez {} secondes".format(
                str(self.engine.max_bet), int(self.engine.betting_delay)))

        if table.shuffled:
            self.send_casino("Le sabot vient d'être mélangé")

    def o_bet(self, player_id):
        self.react_tumb_up(self.last_bet_message_id[player_id])

    def o_cards_distributed(self):
        table = self.engine.table
        response = ["Les jeux sont faits\n",
                    "Première carte de la banque : {} ({})\n".format(str(table.bank_hand),
                                                                     table.bank_hand.readable_value)]
        for player, hand in table.get_hands():  # Todo: put the formatting string in a variable
            response.append("{} : {} ({})".format(player.name, str(hand), hand.max_valid_value))
        response.append("\n/hit pour une nouvelle carte, /stand pour rester, /double pour doubler, /split pour séparer")
        response.append("Vous avez {} secondes".format(int(self.engine.actions_delay)))

        self.send_casino("\n".join(response))
    def on_hit(self, m: MessageEvent):
        self.engine.hit(m.author_id)

    def o_hit(self, player_id, hand):
        self._print_hand(player_id, hand)

    def on_stand(self, m: MessageEvent):
        self.engine.stand(m.author_id)

    def on_double(self, m: MessageEvent):
        self.engine.double(m.author_id)

    def o_double(self, player_id, hand):
        self._print_hand(player_id, hand)

    def on_split(self, m: MessageEvent):
        self.engine.double(m.author_id)

    def o_split(self, player_id, hand, other_hand):
        self._print_hand(player_id, hand)
        self._print_hand(player_id, other_hand)

    def o_end_round(self):
        table = self.engine.table
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
                   "Le but du Blackjack est de tirer des cartes jusqu'à approcher le plus possible de "
                   "21 sans le dépasser",
                   "Le joueur gagne si sa main à plus de valeur que celle de a banque et qu'il n'a pas dépassé 21",
                   "La banque tire en dessous de 17 et reste à 17 ou plus",
                   "",
                   "Les cartes de 2 à 10 valent autant de point", "Les têtes valent 10 points",
                   "L'as vaut 1 ou 11 points à l'avantage du joueur",
                   "",
                   "Un as plus une tête est un Blackjack, et vous rapportera 1,5 fois votre mise en cas de victoire",
                   "Toute combinaison de 3 carte ou plus, même si elle vaut 21 points, "
                   "a moins de valeur qu'un Blackjack",
                   "",
                   "/hit: demande une carte suplémentaire",
                   "/double: double sa mise et demande une dernière carte",
                   "/split: si vous avez une paire, split sépare votre paire en deux jeux indépendants",
                   "/stand: signale que vous ne souhaitez plus de carte"]
        self.client.sendMessage('\n'.join(message), m.author_id)

    def _print_hand(self, player_id, hand):
        player = PCache.get(player_id)
        self.send_casino("{} : {} ({})".format(player.name, str(hand), hand.readable_value))
