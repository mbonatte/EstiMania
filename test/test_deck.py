import unittest
import random

from estimania.deck import Deck

class TestDeck(unittest.TestCase):

    def setUp(self):
        self.deck = Deck()
    
    def test_initial_deck_size(self):
        self.assertEqual(len(self.deck.deck), 52)
        
    def test_suits_in_deck(self):
        suits = set(card.suit for card in self.deck.deck)
        self.assertEqual(suits, {'Hearts', 'Diamonds', 'Clubs', 'Spades'})

    def test_ranks_in_deck(self):
        ranks = set(int(card.value) for card in self.deck.deck)
        self.assertEqual(ranks, set(range(1, 14)))

    def test_shuffle_deck(self):
        deck1 = self.deck.deck.copy()
        random.shuffle(self.deck.deck)
        deck2 = self.deck.deck
        self.assertNotEqual(deck1, deck2)

    def test_deal_cards(self):
        dealt_cards = self.deck.deal(5)
        self.assertEqual(len(dealt_cards), 5)
        self.assertEqual(len(self.deck.deck), 47)

    def test_deal_all_cards(self):
        self.deck.deal(52)
        self.assertEqual(len(self.deck.deck), 0)
        
if __name__ == '__main__':
    unittest.main()