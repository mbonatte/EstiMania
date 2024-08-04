import unittest
from unittest.mock import patch, MagicMock

from estimania.network_player import NetworkPlayer
from estimania.card import Card

class TestPlayer(unittest.TestCase):
    
    @patch('estimania.network_player.emit')
    def setUp(self, mock_emit):
        self.connection_id = "12345"
        self.player = NetworkPlayer(self.connection_id)
    
    @patch('estimania.network_player.emit')
    def test_hand_setter_calls_emit(self, mock_emit):
        new_hand = [Card("9", "Hearts")]
        self.player.hand = new_hand
        mock_emit.assert_called_once_with('hand', [str(card) for card in new_hand], to=self.connection_id)
    
    def test_initialization(self):
        self.assertEqual(self.player.connection_id, self.connection_id)
        self.assertIsNotNone(self.player.username)
        self.assertEqual(self.player.hand, [])
        self.assertEqual(self.player.bet, 0)
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.score_in_turn, 0)

    @patch('estimania.network_player.emit')
    @patch('eventlet.event.Event')
    def test_set_bet(self, mock_event, mock_emit):
        mock_response_event = MagicMock()
        mock_event.return_value = mock_response_event
        mock_response_event.wait.return_value = None
        
        def emit_side_effect(*args, **kwargs):
            callback = kwargs.get('callback')
            if callback:
                callback(1)
        mock_emit.side_effect = emit_side_effect
        
        self.player.set_bet([])

        mock_emit.assert_called_with('bet', self.player.username, to=self.connection_id, callback=unittest.mock.ANY)
        self.assertEqual(self.player.bet, 1)
    
    @patch('estimania.network_player.emit')
    def test_select_card_valid(self, mock_emit):
        cards_in_table = [Card("9", "Hearts")]
        self.player.hand = [Card("10", "Hearts"), Card("5", "Hearts"), Card("2", "Diamonds")]

        def emit_side_effect(*args, **kwargs):
            callback = kwargs.get('callback')
            if callback:
                # Simulate the frontend responding with a valid card
                callback("10 of Hearts")
        
        mock_emit.side_effect = emit_side_effect
        
        card_played = self.player.select_card(cards_in_table)
        
        self.assertEqual(card_played, Card("10", "Hearts"))
        self.assertNotIn(Card("10", "Hearts"), self.player.hand)
        mock_emit.assert_called_with('hand', [str(card) for card in self.player.hand], to=self.connection_id)
    
    @patch('estimania.network_player.emit')
    def test_select_card_invalid(self, mock_emit):
        cards_in_table = [Card("9", "Hearts")]
        self.player.hand = [Card("10", "Hearts"), Card("2", "Hearts")]
        
        def emit_side_effect(*args, **kwargs):
            callback = kwargs.get('callback')
            if callback:
                callback("10 of Diamonds")
        
        mock_emit.side_effect = emit_side_effect
        
        card_played = self.player.select_card(cards_in_table, timeout=0.1)
        
        self.assertFalse(card_played)
        self.assertIn(Card("10", "Hearts"), self.player.hand)
        self.assertIn(Card("2", "Hearts"), self.player.hand)
        mock_emit.assert_any_call('pick', self.player.username, to=self.connection_id, callback=unittest.mock.ANY)
        mock_emit.assert_any_call('error', "Card not valid!", to=self.connection_id)

    @patch('estimania.network_player.emit')
    def test_is_moviment_valid(self, mock_emit):
        cards_in_table = [Card("9", "Hearts")]
        self.player.hand = [Card("10", "Hearts"), Card("2", "Diamonds")]
        
        valid_card = Card("10", "Hearts")
        invalid_card = Card("2", "Diamonds")
        
        self.assertTrue(self.player.is_moviment_valid(valid_card, cards_in_table))
        self.assertFalse(self.player.is_moviment_valid(invalid_card, cards_in_table))

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
