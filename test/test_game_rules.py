import unittest
import random

from estimania.card import Card
from estimania.deck import Deck
from estimania.game_rules import GameRules

# Simple Player stub
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

class TestGameRules(unittest.TestCase):

    def test_build_match_sequence_respects_max_turns_and_deck(self):
        gr = GameRules(max_turns=5)

        # 4 players -> 52//4 = 13, cap at max_turns=5 → [1..5] + [5..1]
        self.assertEqual(
            gr.build_match_sequence(num_players=4),
            [1, 2, 3, 4, 5, 5, 4, 3, 2, 1],
        )

        # 26 players -> 52//26 = 2, cap at 2 → [1,2,2,1]
        self.assertEqual(
            gr.build_match_sequence(num_players=26),
            [1, 2, 2, 1],
        )

        # A lot of players -> 52 // 60 = 0 → empty sequence
        self.assertEqual(
            gr.build_match_sequence(num_players=60),
            [],
        )
    
    def test_build_match_sequence_with_larger_max_turns(self):
        gr = GameRules(max_turns=20)
        # 7 players -> 52//7 = 7 (< max_turns) → [1..7] + [7..1]
        self.assertEqual(
            gr.build_match_sequence(num_players=7),
            [1, 2, 3, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 1],
        )
    
    def test_deal_gives_sorted_hands_desc_and_correct_count(self):
        # Build deterministic fake deck that returns known cards
        # We'll ensure sort order: Diamonds > Spades > Hearts > Clubs,
        # and within a suit Ace (1) is highest.

        players = [Player("A"), Player("B")]
        gr = GameRules()

        random.seed(0)
        gr.deal(players, n_cards=3)

        # Correct number of cards
        self.assertEqual(len(players[0].hand), 3)

        self.assertEqual(
            [str(c) for c in players[0].hand],
            ['7 of Spades', '13 of Hearts', '3 of Clubs'],
        )

        self.assertEqual(
            [str(c) for c in players[1].hand],
            ['3 of Spades', '8 of Hearts', '13 of Clubs'],
        )
        
    def test_evaluate_trick_winner_no_rotation(self):
        gr = GameRules()
        # Cards as played in table order (leader at index 0)
        cards = [
            Card(10, "Spades"),
            Card(9, "Diamonds"),
            Card(12, "Clubs"),
            Card(1, "Hearts"),
        ]
        # Diamonds outrank other suits globally; 9♦ should win
        offset, high = gr.evaluate_trick_winner(cards_in_table=cards, starting_index_player=0)
        self.assertEqual(offset, 1)
        self.assertEqual(str(high), "9 of Diamonds")

    def test_evaluate_trick_winner_with_rotation(self):
        gr = GameRules()
        # Table order before rotation:
        # [3♥, 12♣, A♥, 9♦]; leader is index 2 (A♥)
        cards = [
            Card(3, "Hearts"),
            Card(12, "Clubs"),
            Card(1, "Hearts"),
            Card(9, "Diamonds"),
        ]
        # Rotation should make the list start at A♥:
        # rotated = [A♥, 9♦, 3♥, 12♣]; 9♦ (Diamonds) should win.
        offset, high = gr.evaluate_trick_winner(cards_in_table=cards, starting_index_player=2)
        self.assertEqual(offset, 1)
        self.assertEqual(str(high), "9 of Diamonds")

    def test_evaluate_trick_winner_same_suit_high_card_wins(self):
        gr = GameRules()
        # All Spades except one Clubs; suit hierarchy makes Spades beat Clubs,
        # and within Spades, highest rank (with Ace high) wins.
        cards = [
            Card(5, "Spades"),
            Card(10, "Spades"),   # should win among Spades shown here
            Card(7, "Clubs"),
            Card(3, "Spades"),
        ]
        offset, high = gr.evaluate_trick_winner(cards_in_table=cards, starting_index_player=0)
        self.assertEqual(offset, 1)
        self.assertEqual(str(high), "10 of Spades")

    def test_evaluate_trick_winner_ace_high_within_suit(self):
        gr = GameRules()
        cards = [
            Card(1, "Hearts"),    # Ace Hearts
            Card(13, "Hearts"),   # King Hearts
            Card(12, "Hearts"),
            Card(2, "Hearts"),
        ]
        offset, high = gr.evaluate_trick_winner(cards_in_table=cards, starting_index_player=0)
        self.assertEqual(offset, 0)
        self.assertEqual(str(high), "1 of Hearts")
        
if __name__ == '__main__':
    unittest.main()