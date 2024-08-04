import os
import random
import pickle

from uuid import uuid4

import numpy as np

from .player import Player

# Get the current directory of this script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the file
file_path = os.path.join(current_directory, 'mlp_model.pkl')

# Load weights and biases from the file
with open(file_path, 'rb') as f:
    mlp_data = pickle.load(f)

class CustomMLPRegressor:
    def __init__(self, mlp_data):
        self.feature_names_in_ = mlp_data['features']
        self.coefs_ = mlp_data['coefs']
        self.intercepts_ = mlp_data['intercepts']
    
    def relu(self, x):
        return np.maximum(0, x)

    def predict(self, X):
        layer_input = X
        for i in range(len(self.coefs_) - 1):
            layer_input = self.relu(np.dot(layer_input, self.coefs_[i]) + self.intercepts_[i])
        # The output layer uses the identity function
        output = np.dot(layer_input, self.coefs_[-1]) + self.intercepts_[-1]
        return output

class BotPlayer(Player):
    def __init__(self, room_id=None):
        super().__init__()
        self.room_id = room_id
        self.username = 'BOT - ' + uuid4().hex[:4]
        self.mlp_model = CustomMLPRegressor(mlp_data)

        self.env_data = {feature: -1 for feature in self.mlp_model.feature_names_in_}

    def set_env_data(self, current_bets):
        game_data = {
            'n_adversaries': len(current_bets)-1,
        }
        for i, bet in enumerate(current_bets[:-1]):
            game_data[f'bet_{i+1}'] = bet

        user_data = {}
        for i, card in enumerate(self.hand):
            user_data[f'hand_{i+1}'] = int(card)
        user_data["my_bet"] = -1

        self.env_data = {feature: -1 for feature in self.env_data.keys()}

        # Update self.env_data with values from game_data and user_data
        self.env_data.update(game_data)
        self.env_data.update(user_data)

    def set_bet(self, current_bets):
        self.set_env_data(current_bets)
        self.bet = self.bot_bet_decision(self.env_data)
        self.env_data["my_bet"] = self.bet
        return self.bet
            
    def bot_bet_decision(self, environment_data):
        best_bet = None
        best_reward = float('-inf')

        predicted_rewards = self.predict_bets_reawrd(environment_data)

        for bet, predicted_reward in predicted_rewards.items():
            if predicted_reward > best_reward:
                best_reward = predicted_reward
                best_bet = bet

        return best_bet

    def predict_bets_reawrd(self, environment_data):
        possible_bets = list(range(self.get_possible_bets(environment_data)+1))
        predicted_reward = {}
        for bet in possible_bets:
            environment_data['my_bet'] = bet
            predicted_reward[bet] = self.predict_reward(environment_data)
        return predicted_reward

    def get_possible_bets(self, data):
        count = 0
        for key in sorted(data.keys()):
            if key.startswith('hand_'):
                if data[key] == -1:
                    break
                count += 1
        return count

    def predict_reward(self, environment_data):
        # Update the environment data with new data
        self.env_data.update(environment_data)
        
        # Extract the values of the features keys
        features = [[self.env_data[key] for key in self.mlp_model.feature_names_in_]]
        
        # Predict the reward using the model
        return self.mlp_model.predict(features)[0]
    
    def select_card(self, cards_in_table):
        card_index = random.randint(0, len(self.hand)-1)
        card = self.hand[card_index]
        if self.is_moviment_valid(card, cards_in_table):
            self.hand.remove(card)
            return card
        else:
            return self.select_card(cards_in_table)