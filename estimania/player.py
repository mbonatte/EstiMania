from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self):
        self.hand = []
        self.bet = None
        self.score = 0
        self.score_in_turn = 0

    @abstractmethod
    def set_bet(self):
        pass
            
    @abstractmethod
    def select_card(self, card, cards_in_table):
        pass
            
    def is_moviment_valid(self, card_slected, cards_in_table):
        if len(cards_in_table) == 0:
            return True
        first_card = cards_in_table[0]
        if card_slected.suit == first_card.suit:
            return True
        for card in self.hand:
            if card.suit == first_card.suit:
                return False
        return True
    
    def check_points(self):
        if self.bet == self.score_in_turn:
            if self.bet==0:
                self.score += 1
            else:
                self.score += 2*self.bet
        else:
            self.score -= abs(self.bet-self.score_in_turn)
        self.bet = None
        self.score_in_turn = 0
        