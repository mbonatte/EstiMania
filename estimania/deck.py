import random

from .card import Card

class Deck:
    def __init__(self):
        self.deck = []
        self.suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        self.ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.creat_deck()
        
    def creat_deck(self):
        for suit in self.suits:
            for rank in self.ranks:
                self.deck.append(Card(rank, suit))
        random.shuffle(self.deck)
    
    def deal(self,n_cards):
        cards = []
        for i in range(n_cards):
            cards.append(self.deck.pop(0))
        return cards
        
if __name__ == '__main__':
    socketio.run(app, debug=True)

