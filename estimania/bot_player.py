import random
from uuid import uuid4

from .player import Player

class BotPlayer(Player):
    def __init__(self, room_id=None):
        super().__init__()
        self.room_id = room_id
        self.username = 'BOT - ' + uuid4().hex[:4]

    def set_bet(self):
        self.bet = random.randint(0, len(self.hand))
        return self.bet
            
    def select_card(self, cards_in_table):
        card_index = random.randint(0, len(self.hand)-1)
        card = self.hand[card_index]
        if self.is_moviment_valid(card, cards_in_table):
            self.hand.remove(card)
            return card
        else:
            return self.select_card(cards_in_table)