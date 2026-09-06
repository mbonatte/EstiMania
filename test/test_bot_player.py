import unittest
from estimania.card import Card
from estimania.bot_player import BotPlayer
from estimania.card_play_engine import CardPlayEngine
from estimania.final_round_ai import FinalRoundAI
from estimania.game_rules import GameRules
from estimania.game_engine import GameEngine
from estimania.game_events import GameEvents

class SilentEvents(GameEvents):
    def round_announce(self, text): pass
    def score(self, players): pass
    def turn_of(self, player): pass
    def table(self, cards_str, names): pass
    def trick_winner(self, highest_card): pass
    def final_scores(self, players): pass
    def error(self, player, message): pass
    def private_table(self, viewer, cards_str, other_players): pass

class TestBotPlayer(unittest.TestCase):
    def setUp(self):
        self.bot = BotPlayer("TestBot")

    def test_betting_with_monster_hand(self):
        # 3 boss cards: Ace of Diamonds (52), King of Diamonds (51), Ace of Spades (39)
        self.bot.hand = [
            Card(1, "Diamonds"),
            Card(13, "Diamonds"),
            Card(1, "Spades"),
        ]
        bet = self.bot.set_bet([0, -1])
        # Monster hand should bet at least 2 or 3
        self.assertGreaterEqual(bet, 2)
        self.assertLessEqual(bet, 3)

    def test_betting_with_weak_hand(self):
        # Very weak cards: 2 of Clubs (1), 3 of Clubs (2), 4 of Clubs (3)
        self.bot.hand = [
            Card(2, "Clubs"),
            Card(3, "Clubs"),
            Card(4, "Clubs"),
        ]
        bet = self.bot.set_bet([1, -1])
        # Extremely weak hand should bet 0
        self.assertEqual(bet, 0)

    def test_betting_supports_various_hand_sizes(self):
        # 1 card
        self.bot.hand = [Card(1, "Diamonds")]
        bet1 = self.bot.set_bet([-1])
        self.assertIn(bet1, [0, 1])

        # 7 cards
        self.bot.hand = [
            Card(1, "Diamonds"), Card(10, "Diamonds"),
            Card(5, "Spades"), Card(8, "Spades"),
            Card(2, "Hearts"), Card(6, "Clubs"), Card(9, "Clubs")
        ]
        bet7 = self.bot.set_bet([1, 2, -1])
        self.assertGreaterEqual(bet7, 0)
        self.assertLessEqual(bet7, 7)

    def test_ducking_when_bet_is_zero(self):
        engine = CardPlayEngine()
        # Lead is 10 of Clubs. Hand has 2 of Clubs and 9 of Clubs. Both are safe.
        # When ducking, bot should play the highest safe card (9 of Clubs) to dump it
        # while keeping the lowest (2 of Clubs) for later tricks.
        hand = [Card(2, "Clubs"), Card(9, "Clubs")]
        table = [Card(10, "Clubs")]
        card = engine.select_card(
            hand=hand,
            cards_in_table=table,
            bet=0,
            score_in_turn=0,
            total_players=2,
        )
        self.assertEqual(str(card), "9 of Clubs")

    def test_winning_when_must_win(self):
        engine = CardPlayEngine()
        # Need 1 win, 1 card left. Lead is 5 of Hearts. Hand has 10 of Hearts and 2 of Hearts.
        # Must play winning card: 10 of Hearts.
        hand = [Card(2, "Hearts"), Card(10, "Hearts")]
        table = [Card(5, "Hearts")]
        card = engine.select_card(
            hand=hand,
            cards_in_table=table,
            bet=1,
            score_in_turn=0,
            total_players=2,
        )
        self.assertEqual(str(card), "10 of Hearts")

    def test_sloughing_under_opponent_boss(self):
        engine = CardPlayEngine()
        # Lead is 1 of Diamonds (Ace of Diamonds, value 52).
        # Bot has NO Diamonds: has 13 of Hearts (King of Hearts, value 25) and 2 of Clubs (value 1).
        # Bot wants 0 wins (bet=0, score_in_turn=0).
        # Both cards are lower than Ace of Diamonds.
        # Bot should safely SLOUGH (dump) the 13 of Hearts to avoid getting stuck with it!
        hand = [Card(2, "Clubs"), Card(13, "Hearts")]
        table = [Card(1, "Diamonds")]
        card = engine.select_card(
            hand=hand,
            cards_in_table=table,
            bet=0,
            score_in_turn=0,
            total_players=2,
        )
        self.assertEqual(str(card), "13 of Hearts")

    def test_final_round_probability_calculation(self):
        ai = FinalRoundAI()
        # If opponent card is 2 of Clubs (the lowest possible card in 52 deck)
        opp_cards = [Card(2, "Clubs")]
        p_win = ai.compute_prior_win_probability(opp_cards)
        # All 50 remaining cards in the deck are higher than 2 of Clubs!
        # So p_win must be 1.0 (50 / 50 = 1.0)
        self.assertAlmostEqual(p_win, 1.0)

        # If opponent card is 1 of Diamonds (Ace of Diamonds, the highest card in 52 deck)
        opp_cards = [Card(1, "Diamonds")]
        p_win_ace = ai.compute_prior_win_probability(opp_cards)
        # No remaining card can beat Ace of Diamonds
        self.assertAlmostEqual(p_win_ace, 0.0)

    def test_final_round_bet_decision(self):
        ai = FinalRoundAI()
        # Against lowest card, should bet 1
        self.assertEqual(ai.decide_bet([Card(2, "Clubs")], [0]), 1)
        # Against highest card, should bet 0
        self.assertEqual(ai.decide_bet([Card(1, "Diamonds")], [0]), 0)

    def test_full_game_with_bots(self):
        # Run 5 full games with 4 bots
        for _ in range(5):
            players = [BotPlayer(f"Bot{i}") for i in range(4)]
            rules = GameRules(max_turns=3)
            engine = GameEngine(rules=rules, players=players, events=SilentEvents())
            engine.run()

            # Ensure all players finished with valid scores
            for p in players:
                self.assertIsInstance(p.score, int)

if __name__ == '__main__':
    unittest.main()
