import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

from uuid import uuid4

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_routes import register_test_routes

from estimania.game import Game, send_score, send_final_score
from estimania.network_player import NetworkPlayer
from estimania.bot_player import BotPlayer

# Initialize Flask and Flask-SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['PLAYERS'] = {}
app.config['ROOMS_AVAILABLE'] = {}
socketio = SocketIO(app)

register_test_routes(app, socketio)

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
    app.config['ROOMS_AVAILABLE'][room_id] = []
    
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
    return render_template('browse_rooms.html', rooms=app.config['ROOMS_AVAILABLE'])

@app.route('/rooms/<room_id>')
def room(room_id):
    """
    Route to access a specific room.
    """
    if room_id in app.config['ROOMS_AVAILABLE']:
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
    app.config['PLAYERS'][request.sid] = NetworkPlayer(request.sid, room_id=room_id, username=username)
    app.config['ROOMS_AVAILABLE'][room_id].append(request.sid)
    emit('message', f'{username} has connected!', to=room_id)
    send_score(list(app.config['PLAYERS'].values()), room_id)

@socketio.on('message')
def handle_message(data):
    """
    Handle incoming chat messages.
    """
    player = app.config['PLAYERS'][request.sid]
    emit('message', f'{player.username}: {data["message"]}', to=player.room_id)

@socketio.on('start_game')
def handle_start_game(data):
    """
    Handle the event to start a game in a room.
    """
    if request.sid not in app.config['PLAYERS']:
        return  # Handle cases where the player is not registered
    
    room_id = app.config['PLAYERS'][request.sid].room_id
    
    # Notify players in the room that the game has started
    emit('message', 'The game has started!', to=room_id)
    emit('remove_start_game_btn', '', to=room_id)

    # Gather online players in the room
    online_players_in_room = [app.config['PLAYERS'][sid] for sid in socketio.server.manager.rooms['/'][room_id]]

    # Gather bots in the room
    bots_in_room = [BotPlayer(room_id) for _ in range(data.get('num_bots'))]

    # Gather bots in the room
    total_players_in_room = online_players_in_room + bots_in_room

    max_turns = data.get('max_turns')
    
    # Start the game
    game = Game(room_id, players=total_players_in_room, max_turns=max_turns)
    game.run()

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    """
    if request.sid in app.config['PLAYERS']:
        player = app.config['PLAYERS'][request.sid]
        room_id = player.room_id
        emit('message', f'{player.username} has disconnected!', to=room_id)
        send_score(app.config['PLAYERS'].values(), room_id)
        leave_room(room_id)
        del app.config['PLAYERS'][request.sid]
        app.config['ROOMS_AVAILABLE'][room_id].remove(request.sid)
        if not app.config['ROOMS_AVAILABLE'][player.room_id]:
            del app.config['ROOMS_AVAILABLE'][player.room_id]

if __name__ == '__main__':
    socketio.run(app, debug=True)

