from threading import Event
from typing import List, Optional, Dict
from .player import Player
from .card import Card
from .coach_engine import CoachEngine

class NetworkPlayer(Player):
    def __init__(self, socketio, connection_id, room_id=None, username=None):
        self.socketio = socketio
        self.connection_id = connection_id
        self.room_id = room_id
        self.coach = CoachEngine()
        self.final_round_opponent_cards: List[Card] = []
        self.match_scores: Dict[str, int] = {}
        self.last_bets: List[int] = []
        self.last_table: List[Card] = []
        self.is_connected: bool = True
        self._active_wait_event: Optional[Event] = None
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
    
    def on_match_scores_updated(self, match_scores: Dict[str, int]):
        self.match_scores = dict(match_scores)
        if hasattr(self.coach, 'tracker'):
            self.coach.tracker.set_match_scores(match_scores)

    def on_round_started(self, n_cards: int):
        self.final_round_opponent_cards = []
        if hasattr(self.coach, 'tracker'):
            self.coach.tracker.reset_round()

    def on_bets_placed(self, contracts: Dict[str, int]):
        if hasattr(self.coach, 'tracker'):
            self.coach.tracker.set_opponent_contracts(contracts)

    def on_trick_completed(self, cards_in_table: List[Card], winner_idx: int, highest_card: Card, winner_name: Optional[str] = None):
        if hasattr(self.coach, 'tracker'):
            if cards_in_table:
                lead_suit = cards_in_table[0].suit
                for c in cards_in_table:
                    self.coach.tracker.record_trick_card("unknown", c, lead_suit)
            if winner_name:
                self.coach.tracker.record_trick_winner(winner_name)

    def see_opponents_cards(self, cards_str: List[str], other_players):
        self.final_round_opponent_cards = [
            Card.convert_str_to_Card(c) if isinstance(c, str) else c
            for c in cards_str
        ]

    def disconnect(self):
        """Called when this player has disconnected to avoid blocking the game engine."""
        self.is_connected = False
        if self._active_wait_event is not None:
            self._active_wait_event.set()

    def set_bet(self, bets, timeout=30.0):
        self.last_bets = list(bets)
        try:
            n_adversaries = max(1, len(bets) - 1)
            advice = self.coach.get_bet_recommendations(
                hand=self.hand,
                n_adversaries=n_adversaries,
                current_bets=bets,
                final_round_opp_cards=self.final_round_opponent_cards,
                scores=self.match_scores,
            )
            self.socketio.emit('coach_bet_advice', advice, to=self.connection_id)
        except Exception:
            pass

        response_event = Event()
        self._active_wait_event = response_event
        callback = lambda response: self._handle_bet_response(response, response_event)
        self.socketio.emit('bet', self.username, to=self.connection_id, callback=callback)
        if not response_event.wait(timeout):
            self.bet = 0
        self._active_wait_event = None
    
    def _handle_bet_response(self, bet, response_event):
        self.bet = bet or 0
        response_event.result = self.bet
        response_event.set()
    
    def select_card_with_context(self, cards_in_table, active_names=None, timeout=30.0):
        return self.select_card(cards_in_table, timeout=timeout, active_names=active_names)

    def select_card(self, cards_in_table, timeout=30.0, active_names=None):
        self.last_table = list(cards_in_table)
        try:
            advice = self.coach.get_card_recommendation(
                hand=self.hand,
                cards_in_table=cards_in_table,
                bet=self.bet if self.bet is not None and self.bet >= 0 else 0,
                score_in_turn=self.score_in_turn,
                total_players=len(active_names) if active_names else 4,
                my_name=self.username,
                active_player_names=active_names,
            )
            self.socketio.emit('coach_card_advice', advice, to=self.connection_id)
        except Exception:
            pass

        response_event = Event()
        self._active_wait_event = response_event
        callback = lambda response: self._handle_card_selection(response, response_event, cards_in_table)
        self.socketio.emit('pick', self.username, to=self.connection_id, callback=callback)

        card_played = None
        if response_event.wait(timeout):
            card_played = getattr(response_event, 'result', None)
            if card_played:
                self._update_hand_after_card_selection(card_played)
                self._active_wait_event = None
                return card_played
        else:
            self._handle_timeout()
        self._active_wait_event = None

        # Fallback ONLY if player disconnected mid-turn to unfreeze table
        if not self.is_connected and self.hand:
            valid_cards = [c for c in self.hand if self.is_moviment_valid(c, cards_in_table)]
            if valid_cards:
                fallback_card = min(valid_cards, key=lambda c: int(c))
                self._update_hand_after_card_selection(fallback_card)
                return fallback_card
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