from threading import Event
from .player import Player
from .card import Card

class NetworkPlayer(Player):
    def __init__(self, socketio, connection_id, room_id=None, username=None):
        self.socketio = socketio
        self.connection_id = connection_id
        self.room_id = room_id
        super().__init__(username)

    @property
    def hand(self):
        return self._hand
    
    @hand.setter
    def hand(self, new_hand):
        self._hand = new_hand
        self._emit_hand_update()
    
    def _emit_hand_update(self):
        hand_data = [str(card) for card in self._hand]
        self.socketio.emit('hand', hand_data, to=self.connection_id)
    
    def set_bet(self, bets, timeout=None):
        response_event = Event()
        callback = lambda response: self._handle_bet_response(response, response_event)
        self.socketio.emit('bet', self.username, to=self.connection_id, callback=callback)
        response_event.wait(timeout)
    
    def _handle_bet_response(self, bet, response_event):
        self.bet = bet or 0
        response_event.result = self.bet
        response_event.set()
    
    def select_card(self, cards_in_table, timeout=None):
        response_event = Event()
        callback = lambda response: self._handle_card_selection(response, response_event, cards_in_table)
        self.socketio.emit('pick', self.username, to=self.connection_id, callback=callback)

        if response_event.wait(timeout):
            card_played = getattr(response_event, 'result', None)
            if card_played:
                self._update_hand_after_card_selection(card_played)
                return card_played
        else:
            self._handle_timeout()
        return False
    
    def _handle_card_selection(self, card_str, response_event, cards_in_table):
        card = Card.convert_str_to_Card(card_str)
        if self.is_moviment_valid(card, cards_in_table):
            response_event.result = card
        else:
            self._handle_invalid_card()
            response_event.result = None
        response_event.set()
    
    def _update_hand_after_card_selection(self, card_played):
        self.hand.remove(card_played)
        self.hand = self._hand

    def _handle_invalid_card(self):
        self.socketio.emit('error', "Card not valid!", to=self.connection_id)
    
    def _handle_timeout(self):
        self.socketio.emit('error', "Timeout occurred while waiting for card selection", to=self.connection_id)