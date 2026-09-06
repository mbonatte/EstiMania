import unittest
from estimania.card import Card
from estimania.coach_engine import CoachEngine

class TestCoachEngine(unittest.TestCase):
    def setUp(self):
        self.coach = CoachEngine()

    def test_get_bet_recommendations_strong_hand(self):
        hand = [
            Card('1', 'Diamonds'),   # Ace of Diamonds - strongest card in game
            Card('13', 'Diamonds'),  # King of Diamonds
            Card('2', 'Clubs'),
        ]
        res = self.coach.get_bet_recommendations(hand, n_adversaries=3)
        self.assertIn('recommended_bet', res)
        self.assertIn('win_probabilities', res)
        self.assertIn('tip', res)
        self.assertEqual(res['is_final_round'], False)
        # Should recommend 1 or 2 with high trumps
        self.assertIn(res['recommended_bet'], [1, 2])
        # Win probabilities should contain keys 0, 1, 2, 3
        for b in range(4):
            self.assertIn(str(b), res['win_probabilities'])
        # Probabilities should sum to approximately 100
        total_p = sum(res['win_probabilities'].values())
        self.assertAlmostEqual(total_p, 100, delta=2)

    def test_get_bet_recommendations_weak_hand(self):
        hand = [
            Card('2', 'Clubs'),
            Card('3', 'Clubs'),
            Card('4', 'Hearts'),
        ]
        res = self.coach.get_bet_recommendations(hand, n_adversaries=3)
        # Weak hand should recommend 0
        self.assertEqual(res['recommended_bet'], 0)
        self.assertGreater(res['win_probabilities']['0'], 40)

    def test_get_bet_recommendations_final_round(self):
        # Empty hand in final round with visible opponent cards
        opp_cards = [Card('5', 'Hearts'), Card('7', 'Clubs'), Card('3', 'Spades')]
        res = self.coach.get_bet_recommendations([], n_adversaries=3, final_round_opp_cards=opp_cards)
        self.assertTrue(res['is_final_round'])
        self.assertIn('0', res['win_probabilities'])
        self.assertIn('1', res['win_probabilities'])
        self.assertEqual(res['win_probabilities']['0'] + res['win_probabilities']['1'], 100)

    def test_get_card_recommendation_ducking(self):
        # Quota met: bet 1, won 1
        hand = [Card('2', 'Clubs'), Card('13', 'Diamonds')]
        cards_in_table = [Card('10', 'Clubs')]
        res = self.coach.get_card_recommendation(
            hand=hand,
            cards_in_table=cards_in_table,
            bet=1,
            score_in_turn=1,
            total_players=4
        )
        self.assertEqual(res['recommended_card'], '2 of Clubs')
        self.assertEqual(res['action_type'], 'duck')
        self.assertIn('Quota', res['tip'])

    def test_get_card_recommendation_winning(self):
        # Must win: bet 1, won 0, 1 trick remaining
        hand = [Card('1', 'Diamonds')]
        cards_in_table = [Card('10', 'Diamonds')]
        res = self.coach.get_card_recommendation(
            hand=hand,
            cards_in_table=cards_in_table,
            bet=1,
            score_in_turn=0,
            total_players=4
        )
        self.assertEqual(res['recommended_card'], '1 of Diamonds')
        self.assertEqual(res['action_type'], 'win')
        self.assertIn('Must win', res['tip'])

if __name__ == '__main__':
    unittest.main()
