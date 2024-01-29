import unittest

from estimania.app import Player, Card
from unittest.mock import Mock

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.connection_id = "12345"
        self.player = Player(self.connection_id)

    def test_initialization(self):
        self.assertEqual(self.player.connection_id, self.connection_id)
        self.assertIsNotNone(self.player.username)
        self.assertEqual(self.player.hand, [])
        self.assertEqual(self.player.bet, 0)
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.score_in_turn, 0)

    def test_set_bet(self):
        response_event = Mock()
        self.player.set_bet(10, response_event)
        response_event.send.assert_called_with(10)

    def test_select_card_valid(self):
        response_event = Mock()
        cards_in_table = [Card("9", "Hearts")]
        self.player.hand = [Card("10", "Hearts"), Card("5", "Hearts"), Card("2", "Diamonds")]
        
        card = "10 of Hearts"
        self.player.select_card(card, response_event, cards_in_table)
        response_event.send.assert_called_with(Card("10", "Hearts"))
        self.assertNotIn(Card("10", "Hearts"), self.player.hand)
        self.assertIn(Card("2", "Diamonds"), self.player.hand)
    
    def test_select_card_invalid(self):
        response_event = Mock()
        card = "10 of Diamonds"
        cards_in_table = [Card("9", "Hearts")]
        self.player.hand = [Card("10", "Diamonds"), Card("2", "Hearts")]
        
        # self.player.select_card(card, response_event, cards_in_table)
        # response_event.send.assert_called_with(None)
        # self.assertIn(Card("10", "Diamonds"), self.player.hand)

    def test_is_moviment_valid(self):
        cards_in_table = [Card("9", "Hearts")]
        self.player.hand = [Card("10", "Hearts"), Card("2", "Diamonds")]
        
        card_selected = Card("10", "Hearts")
        self.assertTrue(self.player.is_moviment_valid(card_selected, cards_in_table))
        
        card_selected = Card("2", "Diamonds")
        self.assertFalse(self.player.is_moviment_valid(card_selected, cards_in_table))

    def test_check_points(self):
        self.player.bet = 3
        self.player.score_in_turn = 3
        self.player.check_points()
        self.assertEqual(self.player.score, 6)
        self.assertEqual(self.player.bet, 0)
        self.assertEqual(self.player.score_in_turn, 0)
        
        self.player.score = 0
        self.player.bet = 0
        self.player.score_in_turn = 0
        self.player.check_points()
        self.assertEqual(self.player.score, 1)
        
        self.player.score = 0
        self.player.bet = 5
        self.player.score_in_turn = 2
        self.player.check_points()
        self.assertEqual(self.player.score, -3)
        
        self.player.score = 0
        self.player.bet = 2
        self.player.score_in_turn = 5
        self.player.check_points()
        self.assertEqual(self.player.score, -3)

if __name__ == '__main__':
    unittest.main()
