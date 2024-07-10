from flask import current_app
from flask_socketio import emit

from .deck import Deck

def send_score(players, room_id):
    """
    Emit the current score to players in a room.
    """
    score = [{'name': p.username, 'bet': p.bet, 'wins': p.score_in_turn}
             for p in players if p.room_id == room_id]
    emit('score', score, to=room_id)

def send_final_score(players, room_id):
    scores = []
    for player in players:
        if player.room_id==room_id:
            content = {
                'name': player.username,
                'score': player.score
            }
            scores.append(content)
    scores = sorted(scores, key=lambda d: d['score'], reverse=True)
    emit('final-score', scores, to=room_id)

class Game:

    def __init__(self, room_id, players=None):
        self.room_id = room_id
        self.players = players or [current_app.config['PLAYERS'][sid] for sid in current_app.config['ROOMS_AVAILABLE'][room_id]]
        self.matches = []
        self.cards_in_table = []
        self.current_player_to_bet = -1
        self.current_player_to_drop = 0
    
    def set_matches(self):
        n_matches = 52 // len(self.players)
        self.matches = [i+1 for i in range(n_matches)]
        self.matches += ([i for i in range(n_matches,0,-1)])
    
    def deal(self,n_cards):
        deck = Deck()
        for player in self.players:
            player.hand = sorted(deck.deal(n_cards), reverse=True)
    
    def setBets(self): 
        # Update the current player index to move to the next player
        self.current_player_to_bet = (self.current_player_to_bet + 1) % len(self.players)
        players =  self.players[self.current_player_to_bet:]
        players += self.players[:self.current_player_to_bet]
        for i, player in enumerate(players):
            emit('turn', player.username, to=self.room_id)
            player.set_bet()
            send_score(self.players, self.room_id)
    
    def winner_of_turn(self):
        cards = self.cards_in_table
        drop = self.current_player_to_drop
        cards = cards[len(cards)-drop:]+cards[:len(cards)-drop]
        highest_card = cards[0]
        winner = 0
        
        for i,card in enumerate(cards):
            if card > highest_card:
                highest_card = card
                winner=i
        self.players[winner].score_in_turn += 1
        emit('winner-card', str(highest_card), to=self.room_id)
        send_score(self.players, self.room_id)
        
        # Update the current player index to move to the next player
        self.current_player_to_drop = winner
    
    def play_select_card_turn(self, player, cards_in_table):
        while True:
            card_played = player.select_card(cards_in_table)
            if card_played is False:
                # Either timeout or invalid card. You might want to handle these differently.
                emit('error', "Please select a valid card", to=player.connection_id)
            else:
                # Valid card selected
                return card_played
    
    def turn(self,n_cards): #This should be in the GameOnline class
        # Update the current player index to move to the next player
        self.current_player_to_drop = self.current_player_to_bet
        for turn in range(n_cards):
            self.cards_in_table = []
            players =  self.players[self.current_player_to_drop:]
            players += self.players[:self.current_player_to_drop]
            for player in players:
                emit('turn', player.username, to=self.room_id)
                card_played = self.play_select_card_turn(player, self.cards_in_table)
                
                # Send the new table to players
                self.cards_in_table.append(card_played)
                table = [str(card) for card in self.cards_in_table]
                names = [_.username for _ in players]
                emit('table', {'table': table, 'names': names}, to=self.room_id)
            
            self.winner_of_turn()
    
    def initiateRound(self,n_cards):
        self.deal(n_cards)
        self.setBets()
        self.turn(n_cards)
        for player in self.players:
            player.check_points()
            
    def finalRound(self):
        cards = []
        deck = Deck()
        
        for player in self.players:
            player.hand = deck.deal(1)
            cards.append(player.hand[0])
        
        for player in self.players:
            table = [str(this_player.hand[0]) for this_player in self.players if this_player != player]
            names = [this_player.username for this_player in self.players if this_player != player]
            
            emit('table', {'table': table, 'names': names}, to=player.connection_id)
        
        self.setBets()
        
        highest_card = cards[0]
        winner = 0
        for i,card in enumerate(cards):
            if card > highest_card:
                highest_card = card
                winner=i
        self.players[winner].score_in_turn += 1
        
        for player in self.players:
            player.check_points()

    def run(self):
        self.set_matches()
        while(len(self.matches)!=0):
            if (len(self.matches)==1):
                self.finalRound()
                break
            self.initiateRound(self.matches.pop(0))
        send_final_score(self.players, self.room_id)