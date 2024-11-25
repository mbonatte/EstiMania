from flask import render_template, request, redirect, url_for, jsonify

from flask_socketio import emit

from estimania.network_player import NetworkPlayer
from estimania.bot_player import BotPlayer

def register_test_routes(app, socketio):
    @app.route('/test/')
    def test_default():
        return redirect(url_for('test_scenario', scenario='initial'))

    @app.route('/test/<scenario>')
    def test_scenario(scenario):
        """
        Route to test different game scenarios without playing through the game.
        """
        app.config['ROOMS_AVAILABLE'] = {
            scenario: [],
        }
        return render_template('test_room.html', scenario=scenario)

    @socketio.on('load_test_scenario')
    def handle_test_scenario(scenario):
        """
        Handle loading different test scenarios
        """
        test_scenarios = {
            'initial': create_initial_state,
            'mid_game': create_mid_game_state,
            'end_game': create_end_game_state,
            'betting': create_betting_state,
            'picking': create_picking_state,
            'winner': create_winner_state
        }

        if not scenario or scenario.strip() == "":
            scenario = 'initial'

        if scenario in test_scenarios:
            test_scenarios[scenario](socketio)
        else:
            emit('error', f'Unknown test scenario: {scenario}')

def create_initial_state(socketio):
    """Simulate initial game state"""
    emit('message', 'Welcome to the test game!')
    emit('hand', ['8 of Spades', '12 of Hearts'], to=request.sid)
    
    emit('table', {
        'table': ['10 of Spades', '5 of Hearts'],
        'names': ['Plyaer 1', 'Plyaer 2']
    }, to=request.sid)
    emit('score', [
        {'name': 'Player 1', 'bet': 1, 'wins': 0},
        {'name': 'Bot 1', 'bet': 0, 'wins': 1}
    ])
    emit('round', 'Round 3')

def create_mid_game_state(socketio):
    """Simulate middle of the game"""
    emit('message', 'Mid-game test scenario')
    emit('hand', ['8 of Spades', '12 of Hearts'], to=request.sid)
    emit('table', {
        'table': ['10 of Spades', '5 of Hearts'],
        'names': ['Plyaer 1', 'Plyaer 2']
    }, to=request.sid)
    emit('score', [
        {'name': 'Player 1', 'bet': 1, 'wins': 0},
        {'name': 'Bot 1', 'bet': 0, 'wins': 1}
    ])
    emit('round', 'Round 3')
    emit('turn', 'Player 1')

def create_betting_state(socketio):
    """Simulate betting phase"""
    emit('message', 'Place your bets!')
    emit('hand', ['8 of Spades', '12 of Hearts'], to=request.sid)
    emit('table', {
        'table': ['10 of Spades', '5 of Hearts'],
        'names': ['Plyaer 1', 'Plyaer 2']
    }, to=request.sid)
    emit('score', [
        {'name': 'Player 1', 'bet': None, 'wins': 0},
        {'name': 'Bot 1', 'bet': 2, 'wins': 0},
        {'name': 'Bot 2', 'bet': 1, 'wins': 0}
    ])
    emit('round', 'Round 1')
    emit('bet', 'Player 1')

def create_picking_state(socketio):
    """Simulate card picking phase"""
    emit('message', 'Your turn to play a card!')
    emit('hand', ['8 of Spades', '12 of Hearts'], to=request.sid)
    emit('table', {
        'table': ['10 of Spades', '5 of Hearts'],
        'names': ['Plyaer 1', 'Plyaer 2']
    }, to=request.sid)
    emit('score', [
        {'name': 'Player 1', 'bet': 2, 'wins': 0},
        {'name': 'Bot 1', 'bet': 1, 'wins': 1}
    ])
    emit('round', 'Round 2')
    emit('turn', 'Player 1')

def create_winner_state(socketio):
    """Simulate round winner state"""
    emit('message', 'Round complete!')
    emit('hand', ['8 of Spades', '12 of Hearts'], to=request.sid)
    emit('table', {
        'table': ['10 of Spades', '5 of Hearts'],
        'names': ['Plyaer 1', 'Plyaer 2']
    }, to=request.sid)
    emit('score', [
        {'name': 'Player 1', 'bet': 2, 'wins': 1},
        {'name': 'Bot 1', 'bet': 1, 'wins': 0},
        {'name': 'Bot 2', 'bet': 2, 'wins': 1}
    ])
    emit('round', 'Round 3')
    emit('winner-card', '5 of Hearts')

def create_end_game_state(socketio):
    """Simulate end game state"""
    emit('message', 'Game Over!')
    emit('hand', [])
    emit('table', {
        'table': ['10 of Spades', '5 of Hearts', '2 of Hearts', '3 of Hearts'],
        'names': ['Player 1', 'Bot 1', 'Bot 2', 'Bot 3']
    })
    emit('final-score', [
        {'name': 'Player 1', 'score': 10},
        {'name': 'Bot 1', 'score': 8},
        {'name': 'Bot 2', 'score': 12},
        {'name': 'Bot 3', 'score': 6}
    ])