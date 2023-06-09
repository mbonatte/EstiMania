import time
import random
import eventlet
eventlet.monkey_patch()

from uuid import uuid4

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# Game variables
players = {}
game_started = False
table_cards = []
rooms_available = []
user_rooms = {}  # Dictionary to map session IDs to rooms


@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/home')
def home():
    return render_template('index.html')
    
@app.route('/join_room')
def join_available_room():
    return render_template('join_room.html')

@app.route('/browse_rooms')
def browse_rooms():
    rooms = rooms_available
    return render_template('browse_rooms.html', rooms=rooms)

@app.route('/rooms/<room_id>')
def rooms(room_id):
    if room_id in rooms_available:
        return render_template('room.html', room_id=room_id)
    return jsonify({'error': 'No room found'}), 404

@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    if request.method == 'GET':
        return render_template('create_room.html')
    
    username = request.json['username']
    room_id = request.json['roomName']
    pin = request.json['pin']
    print('room_id:  ',room_id)
    
    if room_id == '':
        # Generate a unique room ID or hash
        room_id = uuid4().hex
    print('room_id:  ',room_id)
    # Add room to rooms available
    rooms_available.append(room_id)

    # Return the room information as a response
    response = {'room_id': room_id}
    return jsonify(response)

@socketio.on('connect')
def handle_connect(): 
    pass
    
@socketio.on('join_room')
def handle_join_room(room_id):
    print(request.sid, room_id)
    join_room(room_id)
    user_rooms[request.sid] = room_id  # Map session ID to room ID

@socketio.on('username_response')
def handle_username_response(username):
    print(request.sid)
    print(user_rooms)
    room_id = user_rooms[request.sid]
    players[request.sid] = Player(request.sid, room_id=room_id, username=username)
    emit('message', f'{username} has connected!', to=room_id)
    handle_score()

@socketio.on('message')
def handle_message(data):
    username = players[request.sid].username
    room_id = players[request.sid].room_id
    message = data['message']
    emit('message', f'{username}: {message}', to=room_id)

@socketio.on('start_game')
def handle_start_game():
    room_id = players[request.sid].room_id
    players_in_room = [players[sid] for sid in socketio.server.manager.rooms['/'][room_id]]
    emit('message', 'The game has started!', to=room_id)
    game = Game(room_id, players_in_room)
    game.run()

@socketio.on('pick_card')
def handle_pick_card(card_picked):
    player = players[request.sid]
    if game_started:
        # Removing the card from player's hand
        player.hand.remove(card_picked)
        table_cards.append(card_picked)
        emit('table', table_cards, to=player.room_id)

@socketio.on('score')
def handle_score():
    room_id = players[request.sid].room_id
    score = [f'{player.username}' for player in players.values() if player.room_id==room_id]
    emit('score', score, to=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in players:
        username = players[request.sid].username
        room_id = players[request.sid].room_id
        del players[request.sid]
        emit('message', f'{username} has disconnected!', to=room_id)
        score = [f'{player.username}' for player in players.values() if player.room_id==room_id]
        emit('score', score, to=room_id)
        leave_room(room_id)
        user_rooms.pop(request.sid, None)

class Game:

    def __init__(self, room_id, players=None):
        self.room_id = room_id
        self.players = players
        self.matches = []
        self.cards_in_table = []
        self.current_player_to_bet = -1
        self.current_player_to_drop = 0
    
    def set_matches(self):
        print(f'Setting matches')
        #from math import trunc
        #n_matches = trunc(52/self.numberOfPlayers)
        n_matches = 4
        self.matches = [i+1 for i in range(n_matches)]
        self.matches += ([i for i in range(n_matches,0,-1)])
    
    def deal(self,n_cards):
        print(f'Dealing cards')
        deck = Deck()
        for player in self.players:
            player.hand = deck.deal(n_cards)
            hand = [str(card) for card in player.hand]
            print(f'Sending cards to {player.username}')
            emit('hand', hand, to=player.connection_id)
        print('Cards dealt')
    
    def setBets(self): 
        # Update the current player index to move to the next player
        self.current_player_to_bet = (self.current_player_to_bet + 1) % len(self.players)
        print(f'Setting bets')
        print("Bets:")
        players =  self.players[self.current_player_to_bet:]
        players += self.players[:self.current_player_to_bet]
        for i, player in enumerate(players):
            # Set up an event to wait for the response or a timeout
            response_event = eventlet.event.Event()
            
            # Create a closure by passing the response_event to the callback function
            callback = lambda response: player.set_bet(response, response_event)
            
            print(f'Waiting betting of {player.username}')
            
            # Emit the 'bet' event to the specific player and pass the callback function
            emit('bet', player.username, to=player.connection_id, callback=callback)
            
            # Wait for the response or timeout after a certain period
            if i == 0:
                #bet = response_event.wait(timeout=10)
                bet = response_event.wait()
            else:
                #bet = response_event.wait(timeout=5)
                bet = response_event.wait()
            
            if bet is None: player.bet = 0
            print('My bet, ', player.username)
            emit('message', f"{player.username}: bet {player.bet}", to=player.room_id)
    
    def winner_of_turn(self):
        print([str(card) for card in self.cards_in_table])
        cards = self.cards_in_table
        drop = self.current_player_to_drop
        print(f'{self.players[drop].username} ({self.current_player_to_drop}) is dropping')
        cards = cards[len(cards)-drop:]+cards[:len(cards)-drop]
        print([str(card) for card in cards])
        highest_card = cards[0]
        winner = 0
        
        for i,card in enumerate(cards):
            if card > highest_card:
                print("Maior - ", card)
                print(i)
                print(i)
                highest_card = card
                winner=i
        self.players[winner].score_in_turn += 1
        print(f'{self.players[winner].username} won this turn')
        print()
        emit('winner-card', str(highest_card), to=self.room_id)
        
        # Update the current player index to move to the next player
        self.current_player_to_drop = winner
    
    def turn(self,n_cards): #This should be in the GameOnline class
        # Update the current player index to move to the next player
        self.current_player_to_drop = self.current_player_to_bet
        for turn in range(n_cards):
            print(f'Selecting cards ({turn+1}/{n_cards})')
            self.cards_in_table = []
            players =  self.players[self.current_player_to_drop:]
            players += self.players[:self.current_player_to_drop]
            for player in players:
                print(f'Waiting picking of {player.username}')
                card_played = None
                while not card_played:
                    # Set up an event to wait for the response or a timeout
                    response_event = eventlet.event.Event()
                    
                    # Create a closure by passing the response_event to the callback function
                    callback = lambda response: player.select_card(response, response_event, self.cards_in_table)
                    
                    # Emit the 'pick' event to the specific player and pass the callback function
                    valid_moviment = emit('pick', player.username, to=player.connection_id, callback=callback)
                
                    # Wait for the response or timeout after a certain period
                    card_played = response_event.wait()
                    print(card_played)
                
                # Overwrite player's hand
                hand = [str(card) for card in player.hand]
                emit('hand', hand, to=player.connection_id)
                
                
                print(' ',player.username, ' - ',card_played)
                
                # Send the new table to players
                self.cards_in_table.append(card_played)
                table = [str(card) for card in self.cards_in_table]
                emit('table', table, to=player.room_id)
            self.winner_of_turn()
    
    def initiateRound(self,n_cards):
        self.deal(n_cards)
        #time.sleep(5)
        self.setBets()
        self.turn(n_cards)
        for player in self.players:
            player.check_points()
            player.print_score()
        score = [f'{player.username}: {player.score}' for player in self.players]
        emit('score', score, to=self.room_id)

    def run(self):
        print(f'Starting game - {self.room_id}')
        self.set_matches()
        while(len(self.matches)!=0):
            print(f'Match {len(self.matches)}')
            self.initiateRound(self.matches.pop(0))
            print('----------------------------------------')
        for player in self.players:
            player.print_score()

class Player:
    def __init__(self, connection_id, room_id=None, username=None):
        self.connection_id = connection_id
        self.room_id = room_id
        if username==None:
            self.username = uuid4().hex
        else:
            self.username = username
        self.hand = []
        self.bet = -1
        self.score = 0
        self.score_in_turn = 0

    def set_bet(self, bet, response_event):
        if (bet==None):
            self.bet = 0
        else:
            self.bet = bet
        # Set the event to signal that the response has been received
        print('My bet, ', self.username)
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
        print()
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
        self.bet = -1
        self.score_in_turn = 0
            
    def print_score(self):
        print(f'{self.username} = {self.score}')
        
        
class Deck:
    def __init__(self):
        self.deck = []
        self.suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        self.ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.creat_deck()
        
    def creat_deck(self):
        for suit in self.suits:
            for rank in self.ranks:
                self.deck.append(Card(rank, suit))
        random.shuffle(self.deck)
    
    def deal(self,n_cards):
        cards = []
        for i in range(n_cards):
            cards.append(self.deck.pop(0))
        return cards
        
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
        print(self, other)
        if self.suit == other.suit:
            if int(self.value) == 1:
                return True
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

if __name__ == '__main__':
    socketio.run(app, debug=True)

