class Card:

    SUITS = {'Clubs': 0, 'Hearts': 13, 'Spades': 26, 'Diamonds': 39}

    @staticmethod
    def convert_str_to_Card(name):
        value, _, suit = name.split()
        return Card(value, suit)
        
    def __init__(self, value, suit):
        self.value = str(value)
        self.suit = str(suit)
        
    def __int__(self):
        value = 13 if int(self.value) == 1 else int(self.value) - 1
        return self.SUITS[self.suit] + value
    
    def __str__ (self):
        return f'{self.value} of {self.suit}'
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return (self.value == other.value and
                    self.suit == other.suit)
        return False

    def __gt__(self,other):
        if self.suit == other.suit:
            if int(self.value) == 1:
                return True
            if int(other.value) == 1:
                return False
            return int(self.value) > int(other.value)
        if self.suit == 'Clubs':
            return False
        if self.suit == 'Diamonds':
            return True
        if self.suit == 'Spades' and other.suit != 'Diamonds':
            return True
        if self.suit == 'Hearts' and other.suit == 'Clubs':
            return True
        return False