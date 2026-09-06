import os
import random
import pickle
from uuid import uuid4
from typing import List, Optional, Dict

import numpy as np

from .player import Player
from .card import Card
from .card_tracker import CardTracker
from .card_play_engine import CardPlayEngine
from .final_round_ai import FinalRoundAI
from .features import extract_hand_features, FEATURE_NAMES

# Get directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Primary trained model path, with fallback to legacy mlp_model.pkl
trained_model_path = os.path.join(current_directory, 'trained_bot_model.pkl')
legacy_model_path = os.path.join(current_directory, 'mlp_model.pkl')
ga_weights_path = os.path.join(current_directory, 'ga_weights.pkl')

if os.path.exists(trained_model_path):
    with open(trained_model_path, 'rb') as f:
        mlp_data = pickle.load(f)
else:
    with open(legacy_model_path, 'rb') as f:
        mlp_data = pickle.load(f)

# Load GA evolved weights if present
ga_weights = None
if os.path.exists(ga_weights_path):
    try:
        with open(ga_weights_path, 'rb') as f:
            ga_weights = pickle.load(f)
    except Exception:
        ga_weights = None

class CustomMLPRegressor:
    def __init__(self, data):
        self.feature_names_in_ = data['features']
        self.coefs_ = data['coefs']
        self.intercepts_ = data['intercepts']
    
    def relu(self, x):
        return np.maximum(0, x)

    def predict(self, X):
        layer_input = np.array(X, dtype=np.float32)
        for i in range(len(self.coefs_) - 1):
            layer_input = self.relu(np.dot(layer_input, self.coefs_[i]) + self.intercepts_[i])
        output = np.dot(layer_input, self.coefs_[-1]) + self.intercepts_[-1]
        return output.flatten()

class BotPlayer(Player):
    def __init__(self, username=None, model_data=None):
        username = username if username else 'BOT - ' + uuid4().hex[:4]
        super().__init__(username)
        data = model_data if model_data is not None else mlp_data
        self.mlp_model = CustomMLPRegressor(data)
        self.ga_weights = ga_weights

        self.tracker = CardTracker()
        self.play_engine = CardPlayEngine(self.tracker)
        if self.ga_weights and 'sabotage_weight' in self.ga_weights:
            self.play_engine.sabotage_weight = self.ga_weights['sabotage_weight']

        self.final_round_ai = FinalRoundAI(self.tracker)
        self.final_round_opponent_cards: List[Card] = []
        self.last_current_bets: List[int] = []
        self.match_scores: Dict[str, int] = {}

        # Legacy env_data support for backwards compatibility
        self.env_data = {feature: -1 for feature in self.mlp_model.feature_names_in_}

    def on_match_scores_updated(self, match_scores: Dict[str, int]):
        """Called at start of each turn with cumulative match standings."""
        self.match_scores = dict(match_scores)
        self.tracker.set_match_scores(match_scores)

    def on_round_started(self, n_cards: int):
        """Called when a new round starts."""
        self.tracker.reset_round()
        self.final_round_opponent_cards = []

    def on_bets_placed(self, contracts: Dict[str, int]):
        """Called after all bets have been placed for the round."""
        self.tracker.set_opponent_contracts(contracts)

    def on_trick_completed(self, cards_in_table: List[Card], winner_idx: int, highest_card: Card, winner_name: Optional[str] = None):
        """Called after each trick finishes to update card memory and trick counts."""
        if cards_in_table:
            lead_suit = cards_in_table[0].suit
            for c in cards_in_table:
                self.tracker.record_trick_card("unknown", c, lead_suit)
        if winner_name:
            self.tracker.record_trick_winner(winner_name)

    def see_opponents_cards(self, cards_str: List[str], other_players):
        """Receive private view of opponents' cards in the final round."""
        self.final_round_opponent_cards = [
            Card.convert_str_to_Card(c) if isinstance(c, str) else c
            for c in cards_str
        ]

    def set_env_data(self, current_bets):
        """Legacy helper for backward compatibility."""
        game_data = {
            'n_adversaries': len(current_bets) - 1,
        }
        for i, bet in enumerate(current_bets[:-1]):
            game_data[f'bet_{i+1}'] = bet

        user_data = {}
        for i, card in enumerate(self.hand):
            user_data[f'hand_{i+1}'] = int(card)
        user_data["my_bet"] = -1

        self.env_data = {feature: -1 for feature in self.env_data.keys()}
        self.env_data.update(game_data)
        self.env_data.update(user_data)

    def set_bet(self, current_bets):
        self.last_current_bets = list(current_bets)
        n_adversaries = max(1, len(current_bets) - 1)
        leader_name = self.tracker.get_leader_name(self.username)
        leader_score = self.match_scores.get(leader_name, self.score) if leader_name else self.score

        # 1. Final Round (Blind Man's Bluff): hand is empty
        if len(self.hand) == 0:
            opp_cards = self.final_round_opponent_cards
            self.bet = self.final_round_ai.decide_bet(
                opponent_cards=opp_cards,
                prior_bets_made=current_bets,
                my_score=self.score,
                leader_score=leader_score,
            )
            return self.bet

        # 2. Regular Round:
        self.tracker.register_my_hand(self.hand)

        if len(self.mlp_model.feature_names_in_) == len(FEATURE_NAMES):
            best_bet = 0
            best_score = float('-inf')
            n_cards = len(self.hand)

            # GA heuristic estimate for ensemble blending
            ga_est = self._ga_estimate_tricks() if self.ga_weights else None
            deficit = leader_score - self.score

            for cand_bet in range(n_cards + 1):
                feats = extract_hand_features(
                    hand=self.hand,
                    n_adversaries=n_adversaries,
                    current_bets=current_bets,
                    cand_bet=cand_bet,
                )
                pred_reward = float(self.mlp_model.predict([feats])[0])

                # Blend with GA prior
                if ga_est is not None:
                    # Penalize distance from GA target
                    ga_dist = abs(cand_bet - ga_est)
                    pred_reward -= 0.45 * ga_dist

                # Catch-up aggressiveness if trailing the leader by > 3 points in turns >= 3
                if deficit > 3 and n_cards >= 3 and cand_bet > 0:
                    catchup_factor = self.ga_weights.get('catchup_aggression', 0.6) if self.ga_weights else 0.5
                    pred_reward += catchup_factor * 0.4 * cand_bet

                if pred_reward > best_score:
                    best_score = pred_reward
                    best_bet = cand_bet

            self.bet = best_bet
            return self.bet

        # Legacy fallback if old mlp_model is loaded
        self.set_env_data(current_bets)
        self.bet = self.bot_bet_decision(self.env_data)
        self.env_data["my_bet"] = self.bet
        return self.bet

    def _ga_estimate_tricks(self) -> float:
        """Estimate tricks using the evolved GA parameters."""
        gw = self.ga_weights
        suit_weights = {
            'Diamonds': gw.get('diamond_weight', 1.25),
            'Spades': gw.get('spade_weight', 0.95),
            'Hearts': gw.get('heart_weight', 0.50),
            'Clubs': gw.get('club_weight', 0.30),
        }
        est = 0.0
        suit_counts = {'Diamonds': 0, 'Spades': 0, 'Hearts': 0, 'Clubs': 0}
        for c in self.hand:
            suit_counts[c.suit] += 1
            sw = suit_weights.get(c.suit, 0.5)
            rank = int(c.value)
            if rank == 1:
                est += 0.85 * sw * gw.get('ace_bonus', 0.6)
            elif rank in [13, 12]:
                est += 0.60 * sw * gw.get('king_queen_bonus', 0.75)
            elif rank >= 9:
                est += 0.35 * sw
            else:
                est += 0.05 * sw

        voids = sum(1 for cnt in suit_counts.values() if cnt <= 1)
        est += voids * gw.get('short_suit_bonus', 0.4) * 0.15
        return est

    def bot_bet_decision(self, environment_data):
        best_bet = None
        best_reward = float('-inf')
        predicted_rewards = self.predict_bets_reward(environment_data)

        for bet, predicted_reward in predicted_rewards.items():
            if predicted_reward > best_reward:
                best_reward = predicted_reward
                best_bet = bet
        return best_bet

    def predict_bets_reward(self, environment_data):
        possible_bets = list(range(self.get_possible_bets(environment_data) + 1))
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
        self.env_data.update(environment_data)
        features = [[self.env_data[key] for key in self.mlp_model.feature_names_in_]]
        return float(self.mlp_model.predict(features)[0])

    def select_card_with_context(self, cards_in_table, active_names: List[str]):
        total_players = len(active_names) if active_names else (len(self.last_current_bets) if self.last_current_bets else 4)
        card = self.play_engine.select_card(
            hand=self.hand,
            cards_in_table=cards_in_table,
            bet=self.bet if self.bet is not None else 0,
            score_in_turn=self.score_in_turn,
            total_players=total_players,
            my_name=self.username,
            active_player_names=active_names,
        )

        if self.is_moviment_valid(card, cards_in_table):
            self.hand.remove(card)
            return card

        # Fallback to any legal card
        for c in list(self.hand):
            if self.is_moviment_valid(c, cards_in_table):
                self.hand.remove(c)
                return c

        return self.hand.pop(0)

    def select_card(self, cards_in_table):
        active_names = list(self.tracker.opponent_contracts.keys()) if self.tracker.opponent_contracts else None
        return self.select_card_with_context(cards_in_table, active_names)