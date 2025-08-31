import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

from uuid import uuid4
import sys, os
import redis

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from estimania.test_routes import register_test_routes
from estimania.game_rules import GameRules
from estimania.game_online import GameOnline, _emit_score
from estimania.network_player import NetworkPlayer
from estimania.bot_player import BotPlayer

# === Config ===
REDIS_URL = "rediss://default:AWJsAAIncDEwNmJiYzQyOTIxMGM0ZWQxODFjNjE0ZjJhMTY4YmQyY3AxMjUxOTY@normal-kiwi-25196.upstash.io:6379"
REDIS_EXPIRE_SECONDS = 3600  # 1 hour

# === App setup ===
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

socketio = SocketIO(app)

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
)

register_test_routes(app, socketio)

# === Utility Functions ===

def save_player(sid, room_id, username):
    key = f'player:{sid}'
    redis_client.hset(key, mapping={
        'sid': sid,
        'room_id': room_id,
        'username': username
    })
    redis_client.expire(key, REDIS_EXPIRE_SECONDS)

def delete_player(sid):
    redis_client.delete(f'player:{sid}')

def add_to_room(room_id, sid):
    redis_client.sadd(f'room:{room_id}:members', sid)
    redis_client.expire(f'room:{room_id}:members', REDIS_EXPIRE_SECONDS)

def get_players_in_room(room_id):
    sids = redis_client.smembers(f'room:{room_id}:members')
    players = []
    for sid in sids:
        data = redis_client.hgetall(f'player:{sid}')
        if data:
            players.append(NetworkPlayer(
                connection_id=data.get('sid'),
                room_id=data.get('room_id'),
                username=data.get('username')
            ))
    return players

# === Routes ===

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
    
    room_id = request.json.get('roomName', uuid4().hex)
    if room_id == '':
        room_id = uuid4().hex
    
    redis_client.sadd('rooms', room_id)
    redis_client.expire('rooms', REDIS_EXPIRE_SECONDS)
    redis_client.delete(f'room:{room_id}:members')
    return jsonify({'room_id': room_id})
    
@app.route('/join_room')
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
    room_ids = redis_client.smembers('rooms')
    rooms_data = {}

    for room_id in room_ids:
        n_players = redis_client.scard(f'room:{room_id}:members')
        rooms_data[room_id] = list(range(n_players))

    return render_template('browse_rooms.html', rooms=rooms_data)

@app.route('/rooms/<room_id>')
def room(room_id):
    """
    Route to access a specific room.
    """
    if redis_client.sismember('rooms', room_id):
        return render_template('room.html', room_id=room_id)
    return jsonify({'error': 'No room found'}), 404

# === WebSocket Events ===

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

    save_player(request.sid, room_id, username)
    add_to_room(room_id, request.sid)
    redis_client.sadd('rooms', room_id)
    redis_client.expire('rooms', REDIS_EXPIRE_SECONDS)
    
    emit('message', f'{username} has connected!', to=room_id)    
    players = get_players_in_room(room_id)
    _emit_score(players, room_id)

@socketio.on('message')
def handle_message(data):
    """
    Handle incoming chat messages.
    """
    player_data = redis_client.hgetall(f'player:{request.sid}')
    if player_data:
        username = player_data['username']
        room_id = player_data['room_id']
        emit('message', f'{username}: {data["message"]}', to=room_id)

@socketio.on('start_game')
def handle_start_game(data):
    """
    Handle the event to start a game in a room.
    """
    player_data = redis_client.hgetall(f'player:{request.sid}')
    if not player_data:
        return  # Handle cases where the player is not registered
    
    room_id = player_data['room_id']
    
    # Notify players in the room that the game has started
    emit('message', 'The game has started!', to=room_id)
    emit('remove_start_game_btn', '', to=room_id)

    # Gather online players in the room
    online_players_in_room = get_players_in_room(room_id)

    # Gather bots in the room
    bots_in_room = [BotPlayer(room_id) for _ in range(data.get('num_bots'))]

    # Gather bots in the room
    total_players_in_room = online_players_in_room + bots_in_room

    max_turns = data.get('max_turns')
    
    # Start the game
    game_rules = GameRules(max_turns=max_turns)
    game = GameOnline(room_id, total_players_in_room, game_rules)
    
    game.run()

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    """
    player_data = redis_client.hgetall(f'player:{request.sid}')
    if not player_data:
        return
    
    room_id = player_data.get('room_id')
    username = player_data.get('username')

    emit('message', f'{username} has disconnected!', to=room_id)
    players = get_players_in_room(room_id)
    _emit_score(players, room_id)
    
    leave_room(room_id)
    delete_player(request.sid)
    redis_client.srem(f'room:{room_id}:members', request.sid)
    
    # If no members left in room, clean up
    if redis_client.scard(f'room:{room_id}:members') == 0:
        redis_client.srem('rooms', room_id)
        redis_client.delete(f'room:{room_id}:members')

if __name__ == '__main__':
    socketio.run(app, debug=True)

