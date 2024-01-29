import unittest

from estimania.app import Card

class TestCard(unittest.TestCase):
    
    def test_card_initialization(self):
        card = Card(10, 'Hearts')
        self.assertEqual(card.value, '10')
        self.assertEqual(card.suit, 'Hearts')
    
    def test_string_to_card(self):
        suit = 'Hearts'
        rank = 1
        text = f'{rank} of {suit}'
        
        card_from_str = Card.convert_str_to_Card(text)
        card = Card(rank, suit)
        
        self.assertEqual(card, card_from_str)
    
    def test_card_string_representation(self):
        suit = 'Hearts'
        rank = 1
        card = Card(rank, suit)
        self.assertEqual(str(card), f'{rank} of {suit}')
    
    def test_equal(self):
        card_1 = Card(1, 'Hearts')
        card_2 = Card(1, 'Hearts')
        self.assertEqual(card_1, card_2)
        
        card_1 = Card(13, 'Diamonds')
        card_2 = Card(13, 'Diamonds')
        self.assertEqual(card_1, card_2)
        
        card_1 = Card(7, 'Clubs')
        card_2 = Card(7, 'Clubs')
        self.assertEqual(card_1, card_2)
        
        card_1 = Card(4, 'Spades')
        card_2 = Card(4, 'Spades')
        self.assertEqual(card_1, card_2)
        
        card_3 = Card(9, 'Spades')
        self.assertFalse(card_1 == card_3)
        
        card_3 = Card(4, 'Hearts')
        self.assertFalse(card_1 == card_3)
        
    def test_greater_lower_ranks(self):
        card_1 = Card(1, 'Clubs')
        card_2 = Card(2, 'Clubs')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(1, 'Hearts')
        card_2 = Card(2, 'Hearts')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(1, 'Spades')
        card_2 = Card(2, 'Spades')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(1, 'Diamonds')
        card_2 = Card(2, 'Diamonds')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(3, 'Clubs')
        card_2 = Card(2, 'Clubs')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(3, 'Hearts')
        card_2 = Card(2, 'Hearts')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(3, 'Spades')
        card_2 = Card(2, 'Spades')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(3, 'Diamonds')
        card_2 = Card(2, 'Diamonds')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
    
    def test_greater_lower_suits(self):        
        card_1 = Card(1, 'Hearts')
        card_2 = Card(1, 'Clubs')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(1, 'Spades')
        card_2 = Card(1, 'Clubs')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(1, 'Diamonds')
        card_2 = Card(1, 'Clubs')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(1, 'Spades')
        card_2 = Card(2, 'Hearts')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(1, 'Diamonds')
        card_2 = Card(13, 'Hearts')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
        card_1 = Card(2, 'Diamonds')
        card_2 = Card(13, 'Spades')
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        
if __name__ == '__main__':
    unittest.main()