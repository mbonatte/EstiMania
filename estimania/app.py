import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

from uuid import uuid4

from .card import Card
from .deck import Deck
from .player import Player

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# Global variables to store player and room information
players = {}
rooms_available = {}


@app.route('/')
@app.route('/home')
@app.route('/about')
def index():
    """
    Route to serve the main page.
    """
    return render_template('index.html')
    
@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    """
    Route to create a new room.
    """
    if request.method == 'GET':
        return render_template('create_room.html')
    
    # Extract room details from the POST request
    room_id = request.json.get('roomName', uuid4().hex)
    if room_id == '':
        room_id = uuid4().hex
    
    # Register the new room
    rooms_available[room_id] = []
    
    # username = request.json['username']
    # pin = request.json['pin']

    # Return the room information as a response
    response = {'room_id': room_id}
    return jsonify(response)
    
app.route('/join_room')
def join_available_room():
    """
    Route to join an available room.
    """
    return render_template('join_room.html')

@app.route('/browse_rooms')
def browse_rooms():
    """
    Route to browse available rooms.
    """
    return render_template('browse_rooms.html', rooms=rooms_available)

@app.route('/rooms/<room_id>')
def room(room_id):
    """
    Route to access a specific room.
    """
    if room_id in rooms_available:
        return render_template('room.html', room_id=room_id)
    return jsonify({'error': 'No room found'}), 404

@socketio.on('connect')
def handle_connect():
    """
    Handle client connection to the WebSocket.
    """
    pass
    
@socketio.on('join_room')
def handle_join_room(room_id, username):
    """
    Handle a player joining a room.
    """
    join_room(room_id)
    players[request.sid] = Player(request.sid, room_id=room_id, username=username)
    rooms_available[room_id].append(request.sid)
    emit('message', f'{username} has connected!', to=room_id)
    send_score(list(players.values()), room_id)

@socketio.on('message')
def handle_message(data):
    """
    Handle incoming chat messages.
    """
    player = players[request.sid]
    emit('message', f'{player.username}: {data["message"]}', to=player.room_id)

@socketio.on('start_game')
def handle_start_game():
    """
    Handle the event to start a game in a room.
    """
    if request.sid not in players:
        return  # Handle cases where the player is not registered
    
    room_id = players[request.sid].room_id
    
    # Notify players in the room that the game has started
    emit('message', 'The game has started!', to=room_id)
    emit('remove_start_game_btn', '', to=room_id)

    # Gather players in the room
    players_in_room = [players[sid] for sid in socketio.server.manager.rooms['/'][room_id]]
    
    # Start the game
    game = Game(room_id, players_in_room)
    game.run()

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    """
    if request.sid in players:
        player = players[request.sid]
        room_id = player.room_id
        emit('message', f'{player.username} has disconnected!', to=room_id)
        send_score(players.values(), room_id)
        leave_room(room_id)
        del players[request.sid]
        rooms_available[room_id].remove(request.sid)
        if not rooms_available[player.room_id]:
            del rooms_available[player.room_id]

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
        self.players = players
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
            hand = [str(card) for card in player.hand]
            emit('hand', hand, to=player.connection_id)
    
    def setBets(self): 
        # Update the current player index to move to the next player
        self.current_player_to_bet = (self.current_player_to_bet + 1) % len(self.players)
        players =  self.players[self.current_player_to_bet:]
        players += self.players[:self.current_player_to_bet]
        for i, player in enumerate(players):
            emit('turn', player.username, to=self.room_id)
            
            # Set up an event to wait for the response or a timeout
            response_event = eventlet.event.Event()
            
            # Create a closure by passing the response_event to the callback function
            callback = lambda response: player.set_bet(response, response_event)
            
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
    
    def turn(self,n_cards): #This should be in the GameOnline class
        # Update the current player index to move to the next player
        self.current_player_to_drop = self.current_player_to_bet
        for turn in range(n_cards):
            self.cards_in_table = []
            players =  self.players[self.current_player_to_drop:]
            players += self.players[:self.current_player_to_drop]
            for player in players:
                emit('turn', player.username, to=self.room_id)
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
                
                # Overwrite player's hand
                hand = [str(card) for card in player.hand]
                emit('hand', hand, to=player.connection_id)
                
                # Send the new table to players
                self.cards_in_table.append(card_played)
                table = [str(card) for card in self.cards_in_table]
                names = [_.username for _ in players]
                emit('table', {'table': table, 'names': names}, to=self.room_id)
            self.winner_of_turn()
    
    def initiateRound(self,n_cards):
        self.deal(n_cards)
        #time.sleep(5)
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

if __name__ == '__main__':
    socketio.run(app, debug=True)

