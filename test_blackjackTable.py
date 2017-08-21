from unittest import TestCase, skip

from BlackjackTable import BlackjackTable, Phase
from Player import Player


class TestBlackjackTable(TestCase):
    def setUp(self):
        self.t = BlackjackTable()
        self.bob = Player("1561")
        self.rick = Player("4575")

    def test_set_table(self):
        self.assertEqual(self.t.phase, Phase.NONE)
        self.assertFalse(self.t.player_contexts)
        self.t.set_table()
        self.assertFalse(self.t.player_contexts)
        self.assertEqual(self.t.phase, Phase.BETTING)

    def test_bet(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        self.assertEqual(self.t.player_contexts[self.bob].bet, 20)
        self.t.bet(self.bob, 30)
        self.assertEqual(self.t.player_contexts[self.bob].bet, 30)
        self.t.bet(self.rick, 20)
        self.assertEqual(self.t.player_contexts[self.bob].bet, 30)
        self.assertEqual(self.t.player_contexts[self.rick].bet, 20)

    def test_initial_distribution(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        self.t.bet(self.rick, 30)
        self.t.initial_distribution()
        bob_ctx = self.t.player_contexts[self.bob].hand_contexts
        rick_ctx = self.t.player_contexts[self.rick].hand_contexts
        self.assertEqual(len(bob_ctx), 1)
        self.assertEqual(len(rick_ctx), 1)
        self.assertEqual(len(bob_ctx[0].hand.cards), 2)
        self.assertEqual(len(rick_ctx[0].hand.cards), 2)
        self.assertEqual(len(self.t.bank_hand.cards), 1)
        self.assertEqual(self.t.phase, Phase.ACTIONS)

    def test_hit(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        bob_ctx = self.t.player_contexts[self.bob].hand_contexts
        self.t.initial_distribution()
        self.t.hit(self.bob)
        self.assertEqual(len(bob_ctx[0].hand.cards), 3)
        self.t.hit(self.bob)

    def test_stand(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        bob_ctx = self.t.player_contexts[self.bob].hand_contexts
        self.t.initial_distribution()
        self.t.stand(self.bob)
        self.t.hit(self.bob)
        self.assertEqual(len(bob_ctx[0].hand.cards), 2)

    @skip("Todo")
    def test_split(self):
        self.fail()

    @skip("Todo")
    def test_double(self):
        self.fail()

    def test_distribute_bank(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        self.t.initial_distribution()
        self.t.distribute_bank()
        self.assertGreaterEqual(max(self.t.bank_hand.value), 17)

    @skip("Todo")
    def test_reward(self):
        self.fail()

    def test_get_hands(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        self.t.bet(self.rick, 30)
        self.t.initial_distribution()
        hands = self.t.get_hands()
        self.assertEqual(len(hands), 2)

    def test_in_game(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        self.assertTrue(self.t.in_game(self.bob))
        self.assertFalse(self.t.in_game(self.rick))

    def test_has_valid_hands(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        self.t.initial_distribution()
        self.assertTrue(self.t.has_valid_hands(self.bob))
        self.t.stand(self.bob)
        self.assertFalse(self.t.has_valid_hands(self.bob))

    def test_dealing_is_over(self):
        self.t.set_table()
        self.t.bet(self.bob, 20)
        self.t.bet(self.rick, 30)
        self.t.initial_distribution()
        self.assertFalse(self.t.dealing_is_over())
        self.t.stand(self.bob)
        self.assertFalse(self.t.dealing_is_over())
        self.t.stand(self.rick)
        self.assertTrue(self.t.dealing_is_over())

    @skip("Todo")
    def test_summary(self):
        self.fail()
