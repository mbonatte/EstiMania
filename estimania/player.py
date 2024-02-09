from flask_socketio import emit

from uuid import uuid4

from .card import Card

class Player:
    def __init__(self, connection_id, room_id=None, username=None):
        self.connection_id = connection_id
        self.room_id = room_id
        if username==None:
            self.username = uuid4().hex
        else:
            self.username = username
        self.hand = []
        self.bet = 0
        self.score = 0
        self.score_in_turn = 0

    def set_bet(self, bet, response_event):
        if (bet==None):
            self.bet = 0
        else:
            self.bet = bet
        # Set the event to signal that the response has been received
        response_event.send(self.bet)
            
    def select_card(self, card, response_event, cards_in_table):
        card = Card.convert_str_to_Card(card)
        if self.is_moviment_valid(card, cards_in_table):
            self.hand.remove(card)
            response_event.send(card)
        else:
            emit('error', "Card not valid!", to=self.connection_id)
            response_event.send(None)
            
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
        self.bet = 0
        self.score_in_turn = 0
        