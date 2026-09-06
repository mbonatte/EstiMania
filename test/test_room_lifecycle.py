import pytest
from uuid import uuid4
from estimania.app import (
    app, socketio, redis_client,
    save_player, add_to_room, cleanup_player_and_room,
    get_active_rooms, get_players_in_room
)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_room_lifecycle_single_player():
    room_id = f"test_room_{uuid4().hex[:8]}"
    sid = f"sid_{uuid4().hex[:8]}"
    username = "Player1"

    # Player joins
    redis_client.sadd('rooms', room_id)
    save_player(sid, room_id, username)
    add_to_room(room_id, sid)

    active = get_active_rooms()
    assert room_id in active
    assert len(active[room_id]) == 1

    # Player leaves
    cleanup_player_and_room(sid, room_id)

    active_after = get_active_rooms()
    assert room_id not in active_after
    assert not redis_client.sismember('rooms', room_id)
    assert redis_client.scard(f'room:{room_id}:members') == 0

def test_room_lifecycle_multi_player():
    room_id = f"test_room_{uuid4().hex[:8]}"
    sid1 = f"sid_{uuid4().hex[:8]}"
    sid2 = f"sid_{uuid4().hex[:8]}"

    redis_client.sadd('rooms', room_id)
    save_player(sid1, room_id, "User1")
    add_to_room(room_id, sid1)
    save_player(sid2, room_id, "User2")
    add_to_room(room_id, sid2)

    active = get_active_rooms()
    assert room_id in active
    assert len(active[room_id]) == 2

    # Player 1 leaves -> room still has 1 player
    cleanup_player_and_room(sid1, room_id)
    active_mid = get_active_rooms()
    assert room_id in active_mid
    assert len(active_mid[room_id]) == 1

    # Player 2 leaves -> room is deleted
    cleanup_player_and_room(sid2, room_id)
    active_end = get_active_rooms()
    assert room_id not in active_end
    assert not redis_client.sismember('rooms', room_id)

def test_ghost_room_auto_pruned():
    room_id = f"test_ghost_{uuid4().hex[:8]}"
    dead_sid = f"dead_sid_{uuid4().hex[:8]}"

    # Add room and a dead SID that has no player:{sid} data
    redis_client.sadd('rooms', room_id)
    redis_client.sadd(f'room:{room_id}:members', dead_sid)

    # get_active_rooms should detect dead SID, prune it, and delete the ghost room
    active = get_active_rooms()
    assert room_id not in active
    assert not redis_client.sismember('rooms', room_id)
    assert not redis_client.exists(f'room:{room_id}:members')

def test_api_leave_room(client):
    room_id = f"test_api_{uuid4().hex[:8]}"
    sid = f"sid_api_{uuid4().hex[:8]}"

    redis_client.sadd('rooms', room_id)
    save_player(sid, room_id, "ApiUser")
    add_to_room(room_id, sid)

    res = client.get('/api/rooms')
    assert res.status_code == 200
    assert room_id in res.get_json()

    # Leave via POST API
    leave_res = client.post('/api/leave_room', json={'sid': sid, 'room_id': room_id})
    assert leave_res.status_code == 200
    assert leave_res.get_json() == {'status': 'ok'}

    res_after = client.get('/api/rooms')
    assert room_id not in res_after.get_json()
    assert not redis_client.sismember('rooms', room_id)

def test_socket_disconnect_prunes_room():
    test_client = socketio.test_client(app)
    sid = list(socketio.server.manager.rooms['/'][None].keys())[0]
    room_id = f"socket_room_{uuid4().hex[:8]}"

    test_client.emit('join_room', room_id, 'SocketUser')
    active = get_active_rooms()
    assert room_id in active

    test_client.disconnect()
    active_after = get_active_rooms()
    assert room_id not in active_after
    assert not redis_client.sismember('rooms', room_id)

def test_pending_room_lifecycle(client):
    room_name = f"pending_room_{uuid4().hex[:8]}"
    res = client.post('/create_room', json={'roomName': room_name})
    assert res.status_code == 200
    created_id = res.get_json()['room_id']

    # Room route can be visited by host
    room_res = client.get(f'/rooms/{created_id}')
    assert room_res.status_code == 200

    # But browse_rooms does not show empty room to other players
    browse_res = client.get('/api/rooms')
    assert created_id not in browse_res.get_json()

