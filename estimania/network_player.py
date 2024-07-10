from threading import Event

from flask_socketio import emit

from uuid import uuid4

from .player import Player
from .card import Card

class NetworkPlayer(Player):
    def __init__(self, connection_id, room_id=None, username=None):
        self.connection_id = connection_id
        self.room_id = room_id
        if username==None:
            self.username = uuid4().hex
        else:
            self.username = username
        super().__init__()
        self._hand = []

    @property
    def hand(self):
        return self._hand
    
    @hand.setter
    def hand(self, new_hand):
        self._hand = new_hand
        emit('hand', [str(card) for card in self._hand], to=self.connection_id)
    
    def set_bet_frontend(self, bet, response_event):
        if (bet==None):
            self.bet = 0
        else:
            self.bet = bet
        
        response_event.result = self.bet
        response_event.set()
            
    
    def set_bet(self, timeout=5):       
        # Set up an event to wait for the response or a timeout
        response_event = Event()
        
        # Create a closure by passing the response_event to the callback function
        callback = lambda response: self.set_bet_frontend(response, response_event)
        
        # Emit the 'bet' event to the specific player and pass the callback function
        emit('bet', self.username, to=self.connection_id, callback=callback)
        
        # Wait for the response or timeout after a certain period
        response_event.wait()
    
    
    def select_card_frontend(self, card, response_event, cards_in_table):
        card = Card.convert_str_to_Card(card)
        if self.is_moviment_valid(card, cards_in_table):
            self._hand.remove(card)
            response_event.result = card
        else:
            emit('error', "Card not valid!", to=self.connection_id)
            response_event.result = None
        response_event.set()
    
    def select_card(self, cards_in_table, timeout=5):
        # Set up an event to wait for the response or a timeout
        response_event = Event()

        # Create a closure by passing the response_event to the callback function
        def callback(response):
            self.select_card_frontend(response, response_event, cards_in_table)
        
        # Emit the 'pick' event to the specific player and pass the callback function
        emit('pick', self.username, to=self.connection_id, callback=callback)

        # Wait for the response or timeout after a certain period
        if response_event.wait(timeout):
            card_played = getattr(response_event, 'result', None)
        else:
            # Timeout occurred
            emit('error', "Timeout occurred while waiting for card selection", to=self.connection_id)
            return False # Indicate timeout
        
        # Overwrite player's hand
        if card_played:
            self.hand = self._hand
            return card_played
        else:
            return False # Indicate invalid selection