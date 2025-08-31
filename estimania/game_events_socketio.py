# events_socketio.py
from estimania.game_events import GameEvents

class GameSocketEvents(GameEvents):
    def __init__(self, socketio, room_id: str):
        self.socketio = socketio
        self.room_id = room_id

    def round_announce(self, text): self.socketio.emit('round', text, to=self.room_id)
    def score(self, players):
        payload = [{'name': p.username, 'bet': p.bet, 'wins': p.score_in_turn} for p in players]
        self.socketio.emit('score', payload, to=self.room_id)
    def turn_of(self, player): self.socketio.emit('turn', player.username, to=self.room_id)
    def table(self, cards_str, names): self.socketio.emit('table', {'table': cards_str, 'names': names}, to=self.room_id)
    def trick_winner(self, highest_card): self.socketio.emit('winner-card', str(highest_card), to=self.room_id)
    def final_scores(self, players):
        scores = [{'name': p.username, 'score': p.score}
              for p in players if getattr(p, 'room_id', self.room_id) == self.room_id]
        scores = sorted(scores, key=lambda d: d['score'], reverse=True)
        self.socketio.emit('final-score', scores, to=self.room_id)
    def error(self, player, message):
        target = getattr(player, 'connection_id', None) or self.room_id
        self.socketio.emit('error', message, to=target)
    def private_table(self, viewer, cards_str, other_players):
        target = getattr(viewer, 'connection_id', None)
        names = [p.username for p in other_players]
        if target:
            self.socketio.emit('table', {'table': cards_str, 'names': names}, to=target)
