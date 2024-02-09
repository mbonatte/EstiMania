class Card:

    def convert_str_to_Card(name):
        value = name.split()[0]
        suit = name.split()[2]
        return Card(value, suit)
        
    def __init__(self, value, suit):
        self.value = str(value)
        self.suit = str(suit)
        
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
            if int(self.value) > int(other.value):
                return True
            else:
                return False
        else:
            if self.suit == 'Clubs':
                return False
            if self.suit == 'Diamonds':
                return True
            if self.suit == 'Spades' and other.suit != 'Diamonds':
                return True
            if self.suit == 'Hearts' and other.suit == 'Clubs':
                return True
            return False