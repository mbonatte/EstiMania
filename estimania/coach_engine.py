import os
import pickle
from typing import List, Dict, Optional, Any
import numpy as np

from estimania.card import Card
from estimania.features import extract_hand_features
from estimania.card_play_engine import CardPlayEngine
from estimania.card_tracker import CardTracker
from estimania.final_round_ai import FinalRoundAI
from estimania.bot_player import CustomMLPRegressor, trained_model_path, legacy_model_path, ga_weights

class CoachEngine:
    """
    Advisor and Coach engine for EstiMania.
    Provides:
    - Real-time win / success probabilities for all candidate bets (0..N).
    - Educational rationale explaining why the recommended bet is optimal.
    - Card recommendations for the current trick with strategic explanations.
    """

    def __init__(self, tracker: Optional[CardTracker] = None):
        self.tracker = tracker or CardTracker()
        self.play_engine = CardPlayEngine(self.tracker)
        self.final_round_ai = FinalRoundAI(self.tracker)
        self.ga_weights = ga_weights

        # Load trained MLP model for trick evaluation
        data = None
        if os.path.exists(trained_model_path):
            with open(trained_model_path, 'rb') as f:
                data = pickle.load(f)
        elif os.path.exists(legacy_model_path):
            with open(legacy_model_path, 'rb') as f:
                data = pickle.load(f)

        self.mlp_model = CustomMLPRegressor(data) if data else None

    def _ga_estimate_tricks(self, hand: List[Card]) -> float:
        """Estimate expected tricks using GA evolved parameters."""
        gw = self.ga_weights or {}
        suit_weights = {
            'Diamonds': gw.get('diamond_weight', 1.45),
            'Spades': gw.get('spade_weight', 1.15),
            'Hearts': gw.get('heart_weight', 0.35),
            'Clubs': gw.get('club_weight', 0.34),
        }
        est = 0.0
        suit_counts = {'Diamonds': 0, 'Spades': 0, 'Hearts': 0, 'Clubs': 0}
        for c in hand:
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

    def get_bet_recommendations(
        self,
        hand: List[Card],
        n_adversaries: int,
        current_bets: Optional[List[int]] = None,
        final_round_opp_cards: Optional[List[Card]] = None,
        scores: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Calculates win probability percentage for each candidate bet (0..N),
        the recommended bet, and a helpful coach explanation.
        """
        n_adversaries = max(1, n_adversaries)
        current_bets = current_bets or ([-1] * (n_adversaries + 1))

        # Case 1: Final Round (Blind Man's Bluff - hand is empty)
        if len(hand) == 0:
            opp_cards = final_round_opp_cards or []
            p_win = self.final_round_ai.bayesian_posterior_win_probability(
                opponent_cards=opp_cards,
                prior_bets_made=current_bets,
            )
            pct_win = max(1, min(99, int(round(p_win * 100))))
            pct_zero = 100 - pct_win
            recommended_bet = 1 if pct_win >= 50 else 0

            highest_opp = max(opp_cards, key=lambda c: int(c)) if opp_cards else None
            opp_str = f"opponents' top card is {highest_opp}" if highest_opp else "opponents' visible cards"

            if recommended_bet == 1:
                tip = f"Your unseen card has a strong {pct_win}% chance to beat {opp_str}! Bidding 1 is favored."
            else:
                tip = f"With {opp_str}, your win probability is {pct_win}%. Bidding 0 is safer."

            return {
                "recommended_bet": recommended_bet,
                "win_probabilities": {"0": pct_zero, "1": pct_win},
                "tip": tip,
                "is_final_round": True,
            }

        # Case 2: Regular Round
        n_cards = len(hand)
        ga_est = self._ga_estimate_tricks(hand)
        scores_list = []

        for cand_bet in range(n_cards + 1):
            if self.mlp_model is not None:
                feats = extract_hand_features(
                    hand=hand,
                    n_adversaries=n_adversaries,
                    current_bets=current_bets,
                    cand_bet=cand_bet,
                )
                pred_reward = float(self.mlp_model.predict([feats])[0])
            else:
                pred_reward = 0.0

            # Blend with GA prior distance penalty
            ga_dist = abs(cand_bet - ga_est)
            score = pred_reward - 0.45 * ga_dist
            scores_list.append(score)

        # Calibrate via temperature-scaled softmax
        scores_arr = np.array(scores_list, dtype=np.float64)
        temperature = 1.25
        exp_vals = np.exp((scores_arr - np.max(scores_arr)) / temperature)
        raw_probs = exp_vals / np.sum(exp_vals)

        # Convert to integer percentages that sum to 100
        int_probs = [int(round(p * 100)) for p in raw_probs]
        # Adjust rounding difference to ensure sum == 100
        diff = 100 - sum(int_probs)
        if diff != 0:
            best_idx = int(np.argmax(raw_probs))
            int_probs[best_idx] += diff

        # Ensure minimum 1% display for visibility if prob > 0
        for i in range(len(int_probs)):
            if int_probs[i] == 0 and raw_probs[i] > 0.005:
                int_probs[i] = 1

        rec_bet = int(np.argmax(scores_arr))
        rec_prob = int_probs[rec_bet]

        # Generate descriptive coach rationale
        diamond_cards = [c for c in hand if c.suit == 'Diamonds']
        spade_cards = [c for c in hand if c.suit == 'Spades']
        high_trumps = [c for c in hand if c.suit in ['Diamonds', 'Spades'] and int(c.value) in [1, 13, 12]]

        card_hints = []
        if high_trumps:
            trump_names = [f"{c.value} of {c.suit}" for c in high_trumps[:2]]
            card_hints.append(f"top cards ({', '.join(trump_names)})")
        elif diamond_cards:
            card_hints.append(f"{len(diamond_cards)} Diamond trump(s)")
        elif spade_cards:
            card_hints.append(f"{len(spade_cards)} Spade(s)")

        if rec_bet == 0:
            if card_hints:
                tip = f"Bidding 0 is safest ({rec_prob}% confidence). Your hand lacks dominant winners."
            else:
                tip = f"Bidding 0 has the highest success chance ({rec_prob}%). Stay low and duck tricks."
        else:
            hint_str = f" With your {' and '.join(card_hints)}," if card_hints else ""
            tip = f"{hint_str} bidding {rec_bet} is your strongest contract with a {rec_prob}% success rate."

        prob_dict = {str(b): int_probs[b] for b in range(n_cards + 1)}

        return {
            "recommended_bet": rec_bet,
            "win_probabilities": prob_dict,
            "tip": tip.strip(),
            "is_final_round": False,
        }

    def get_card_recommendation(
        self,
        hand: List[Card],
        cards_in_table: List[Card],
        bet: int,
        score_in_turn: int,
        total_players: int = 4,
        my_name: str = "Player",
        active_player_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Determines the optimal card to play from hand, along with an intuitive explanation.
        """
        legal = self.play_engine.get_legal_cards(hand, cards_in_table)
        if not legal:
            return {
                "recommended_card": str(hand[0]) if hand else None,
                "tip": "No cards remaining.",
                "action_type": "none",
            }

        rec_card = self.play_engine.select_card(
            hand=hand,
            cards_in_table=cards_in_table,
            bet=bet,
            score_in_turn=score_in_turn,
            total_players=total_players,
            my_name=my_name,
            active_player_names=active_player_names,
        )

        needed_wins = bet - score_in_turn
        remaining_tricks = len(hand)
        is_leading = len(cards_in_table) == 0
        lead_suit = cards_in_table[0].suit if not is_leading else None
        current_highest = max(cards_in_table, key=lambda c: int(c)) if not is_leading else None

        card_str = str(rec_card)
        rank_name = rec_card.value
        if rank_name == '1':
            rank_display = f"Ace of {rec_card.suit}"
        elif rank_name == '13':
            rank_display = f"King of {rec_card.suit}"
        elif rank_name == '12':
            rank_display = f"Queen of {rec_card.suit}"
        elif rank_name == '11':
            rank_display = f"Jack of {rec_card.suit}"
        else:
            rank_display = card_str

        # Generate strategic rationale
        if needed_wins <= 0:
            action_type = "duck"
            if is_leading:
                tip = f"Quota reached ({score_in_turn}/{bet}). Lead low {rank_display} to avoid taking the trick."
            elif current_highest and int(rec_card) < int(current_highest):
                tip = f"Quota secured ({score_in_turn}/{bet}). Play {rank_display} under the table to stay safe."
            else:
                tip = f"Quota met! Play {rank_display} to minimize risk."

        elif needed_wins >= remaining_tricks:
            action_type = "win"
            if is_leading:
                tip = f"Must win remaining trick(s)! Lead your powerful {rank_display} to control the round."
            elif current_highest and int(rec_card) > int(current_highest):
                tip = f"Must win this trick! Play {rank_display} to beat current highest ({current_highest})."
            else:
                tip = f"Cannot overtake the table. Save higher cards with {rank_display}."

        else:
            # Balanced play (0 < needed_wins < remaining_tricks)
            if is_leading:
                action_type = "lead"
                if rec_card.suit == 'Diamonds' and int(rec_card.value) in [1, 13, 12]:
                    tip = f"Cash your boss {rank_display} to guarantee 1 of your {needed_wins} needed trick(s)."
                else:
                    tip = f"Lead {rank_display} to test opponents' trumps without burning your high cards."
            else:
                if lead_suit and rec_card.suit != lead_suit and int(rec_card) > int(current_highest):
                    action_type = "trump"
                    tip = f"Void in {lead_suit}! Trump with {rank_display} to steal this trick for your contract."
                elif lead_suit and rec_card.suit != lead_suit:
                    action_type = "slough"
                    tip = f"Void in {lead_suit}! Slough off {rank_display} safely."
                elif int(rec_card) > int(current_highest):
                    action_type = "win"
                    tip = f"Play {rank_display} to capture this trick ({score_in_turn + 1}/{bet} needed)."
                else:
                    action_type = "duck"
                    tip = f"Hold your trump power: duck with {rank_display} under {current_highest}."

        return {
            "recommended_card": card_str,
            "tip": tip,
            "action_type": action_type,
            "needed_wins": needed_wins,
            "remaining_tricks": remaining_tricks,
        }
