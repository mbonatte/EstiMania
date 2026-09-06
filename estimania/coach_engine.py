import os
import random
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

        # Helper card formatter
        def fmt_card_pt(c: Card) -> str:
            val_map = {'1': 'Ás', '13': 'Rei', '12': 'Dama', '11': 'Valete'}
            suit_map = {'Diamonds': 'Ouros', 'Spades': 'Espadas', 'Hearts': 'Copas', 'Clubs': 'Paus'}
            v = val_map.get(c.value, c.value)
            s = suit_map.get(c.suit, c.suit)
            return f"{v} de {s}"

        def fmt_suit_pt(suit: str) -> str:
            return {'Diamonds': 'Ouros', 'Spades': 'Espadas', 'Hearts': 'Copas', 'Clubs': 'Paus'}.get(suit, suit)

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
            opp_str_en = f"opponents' top card is {highest_opp}" if highest_opp else "opponents' visible cards"
            opp_str_pt = f"a carta mais alta dos oponentes é {fmt_card_pt(highest_opp)}" if highest_opp else "as cartas visíveis dos oponentes"

            if recommended_bet == 1:
                tip_en = f"Your unseen card has a strong {pct_win}% chance to beat {opp_str_en}! Bidding 1 is favored."
                tip_pt = f"Sua carta oculta tem {pct_win}% de chance de vencer {opp_str_pt}! Apostar 1 é a melhor escolha."
            else:
                tip_en = f"With {opp_str_en}, your win probability is {pct_win}%. Bidding 0 is safer."
                tip_pt = f"Com {opp_str_pt}, sua chance de vitória é de {pct_win}%. Apostar 0 é mais seguro."

            return {
                "recommended_bet": recommended_bet,
                "win_probabilities": {"0": pct_zero, "1": pct_win},
                "tip": tip_en,
                "tip_pt": tip_pt,
                "is_final_round": True,
            }

        # Case 2: Regular Round
        n_cards = len(hand)
        unseen = self.tracker.get_unseen_cards(hand)
        total_opp_cards = n_adversaries * n_cards

        if len(unseen) >= total_opp_cards:
            actual_samples = min(60, 60 if n_cards <= 4 else 35)
            win_counts = {w: 0 for w in range(n_cards + 1)}
            total_players = n_adversaries + 1

            for _ in range(actual_samples):
                shuffled = list(unseen)
                random.shuffle(shuffled)
                opp_hands = [shuffled[i * n_cards : (i + 1) * n_cards] for i in range(n_adversaries)]

                my_h = list(hand)
                sim_hands = [my_h] + [list(h) for h in opp_hands]
                leader = 0
                my_wins = 0

                for _ in range(n_cards):
                    order = list(range(leader, total_players)) + list(range(0, leader))
                    trick = []
                    for p_idx in order:
                        h = sim_hands[p_idx]
                        if not trick:
                            c = max(h, key=lambda x: int(x)) if any(int(x) >= 48 for x in h) else min(h, key=lambda x: int(x))
                        else:
                            lead_suit = trick[0].suit
                            legal = [x for x in h if x.suit == lead_suit] or h
                            cur_high = max(int(x) for x in trick)
                            winners = [x for x in legal if int(x) > cur_high]
                            if winners:
                                c = min(winners, key=lambda x: int(x))
                            else:
                                c = min(legal, key=lambda x: int(x))
                        h.remove(c)
                        trick.append(c)

                    best_c = max(trick, key=lambda x: int(x))
                    win_pos = trick.index(best_c)
                    leader = order[win_pos]
                    if leader == 0:
                        my_wins += 1

                win_counts[my_wins] += 1

            raw_probs = [win_counts.get(w, 0) / actual_samples for w in range(n_cards + 1)]

            # Compute Expected Values for optimal contract selection
            evs = []
            for b in range(n_cards + 1):
                ev = 0.0
                for w in range(n_cards + 1):
                    p = raw_probs[w]
                    rew = (1.0 if b == 0 else 2.0 * b) if w == b else -float(abs(b - w))
                    ev += p * rew
                evs.append(ev)

            rec_bet = int(np.argmax(evs))
        else:
            raw_probs = [1.0] + [0.0] * n_cards
            rec_bet = 0

        # Convert to integer percentages that sum to 100
        int_probs = [int(round(p * 100)) for p in raw_probs]
        diff = 100 - sum(int_probs)
        if diff != 0:
            best_idx = int(np.argmax(raw_probs))
            int_probs[best_idx] += diff

        for i in range(len(int_probs)):
            if int_probs[i] == 0 and raw_probs[i] > 0.005:
                int_probs[i] = 1

        rec_prob = int_probs[rec_bet]

        # Generate descriptive coach rationale
        diamond_cards = [c for c in hand if c.suit == 'Diamonds']
        spade_cards = [c for c in hand if c.suit == 'Spades']
        high_trumps = [c for c in hand if c.suit in ['Diamonds', 'Spades'] and int(c.value) in [1, 13, 12]]

        card_hints_en = []
        card_hints_pt = []
        if high_trumps:
            trump_names_en = [f"{c.value} of {c.suit}" for c in high_trumps[:2]]
            trump_names_pt = [fmt_card_pt(c) for c in high_trumps[:2]]
            card_hints_en.append(f"top cards ({', '.join(trump_names_en)})")
            card_hints_pt.append(f"cartas altas ({', '.join(trump_names_pt)})")
        elif diamond_cards:
            card_hints_en.append(f"{len(diamond_cards)} Diamond trump(s)")
            card_hints_pt.append(f"{len(diamond_cards)} trunfo(s) de Ouros")
        elif spade_cards:
            card_hints_en.append(f"{len(spade_cards)} Spade(s)")
            card_hints_pt.append(f"{len(spade_cards)} Espada(s)")

        if rec_bet == 0:
            if card_hints_en:
                tip_en = f"Bidding 0 is safest ({rec_prob}% confidence). Your hand lacks dominant winners."
                tip_pt = f"Apostar 0 é mais seguro ({rec_prob}% de confiança). Sua mão não possui cartas dominantes."
            else:
                tip_en = f"Bidding 0 has the highest success chance ({rec_prob}%). Stay low and duck tricks."
                tip_pt = f"Apostar 0 tem a maior chance de sucesso ({rec_prob}%). Jogue baixo para não levar vazas."
        else:
            hint_str_en = f" With your {' and '.join(card_hints_en)}," if card_hints_en else ""
            hint_str_pt = f" Com seus {' e '.join(card_hints_pt)}," if card_hints_pt else ""
            tip_en = f"{hint_str_en} bidding {rec_bet} is your strongest contract with a {rec_prob}% success rate."
            tip_pt = f"{hint_str_pt} apostar {rec_bet} é seu melhor palpite com {rec_prob}% de chance de sucesso."

        prob_dict = {str(b): int_probs[b] for b in range(n_cards + 1)}

        return {
            "recommended_bet": rec_bet,
            "win_probabilities": prob_dict,
            "tip": tip_en.strip(),
            "tip_pt": tip_pt.strip(),
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
                "tip_pt": "Nenhuma carta restante.",
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
        val_map_pt = {'1': 'Ás', '13': 'Rei', '12': 'Dama', '11': 'Valete'}
        suit_map_pt = {'Diamonds': 'Ouros', 'Spades': 'Espadas', 'Hearts': 'Copas', 'Clubs': 'Paus'}

        if rank_name == '1':
            rank_display_en = f"Ace of {rec_card.suit}"
            rank_display_pt = f"Ás de {suit_map_pt.get(rec_card.suit, rec_card.suit)}"
        elif rank_name == '13':
            rank_display_en = f"King of {rec_card.suit}"
            rank_display_pt = f"Rei de {suit_map_pt.get(rec_card.suit, rec_card.suit)}"
        elif rank_name == '12':
            rank_display_en = f"Queen of {rec_card.suit}"
            rank_display_pt = f"Dama de {suit_map_pt.get(rec_card.suit, rec_card.suit)}"
        elif rank_name == '11':
            rank_display_en = f"Jack of {rec_card.suit}"
            rank_display_pt = f"Valete de {suit_map_pt.get(rec_card.suit, rec_card.suit)}"
        else:
            rank_display_en = card_str
            rank_display_pt = f"{rank_name} de {suit_map_pt.get(rec_card.suit, rec_card.suit)}"

        lead_suit_pt = suit_map_pt.get(lead_suit, lead_suit) if lead_suit else ""
        current_highest_pt = ""
        if current_highest:
            ch_val = val_map_pt.get(current_highest.value, current_highest.value)
            ch_suit = suit_map_pt.get(current_highest.suit, current_highest.suit)
            current_highest_pt = f"{ch_val} de {ch_suit}"

        # Generate strategic rationale
        if needed_wins <= 0:
            action_type = "duck"
            if is_leading:
                tip_en = f"Quota reached ({score_in_turn}/{bet}). Lead low {rank_display_en} to avoid taking the trick."
                tip_pt = f"Meta atingida ({score_in_turn}/{bet}). Puxe {rank_display_pt} baixo para evitar levar a vaza."
            elif current_highest and int(rec_card) < int(current_highest):
                tip_en = f"Quota secured ({score_in_turn}/{bet}). Play {rank_display_en} under the table to stay safe."
                tip_pt = f"Meta garantida ({score_in_turn}/{bet}). Jogue {rank_display_pt} abaixo da mesa para ficar seguro."
            else:
                tip_en = f"Quota met! Play {rank_display_en} to minimize risk."
                tip_pt = f"Meta cumprida! Jogue {rank_display_pt} para minimizar riscos."

        elif needed_wins >= remaining_tricks:
            action_type = "win"
            if is_leading:
                tip_en = f"Must win remaining trick(s)! Lead your powerful {rank_display_en} to control the round."
                tip_pt = f"Precisa vencer as vazas restantes! Puxe {rank_display_pt} para controlar a rodada."
            elif current_highest and int(rec_card) > int(current_highest):
                tip_en = f"Must win this trick! Play {rank_display_en} to beat current highest ({current_highest})."
                tip_pt = f"Precisa vencer esta vaza! Jogue {rank_display_pt} para superar a carta mais alta ({current_highest_pt})."
            else:
                tip_en = f"Cannot overtake the table. Save higher cards with {rank_display_en}."
                tip_pt = f"Não é possível superar a mesa. Poupe cartas maiores com {rank_display_pt}."

        else:
            # Balanced play (0 < needed_wins < remaining_tricks)
            if is_leading:
                action_type = "lead"
                if rec_card.suit == 'Diamonds' and int(rec_card.value) in [1, 13, 12]:
                    tip_en = f"Cash your boss {rank_display_en} to guarantee 1 of your {needed_wins} needed trick(s)."
                    tip_pt = f"Jogue seu {rank_display_pt} para garantir 1 das suas {needed_wins} vaza(s) necessárias."
                else:
                    tip_en = f"Lead {rank_display_en} to test opponents' trumps without burning your high cards."
                    tip_pt = f"Puxe {rank_display_pt} para testar os trunfos adversários sem gastar cartas altas."
            else:
                if lead_suit and rec_card.suit != lead_suit and int(rec_card) > int(current_highest):
                    action_type = "trump"
                    tip_en = f"Void in {lead_suit}! Trump with {rank_display_en} to steal this trick for your contract."
                    tip_pt = f"Sem cartas de {lead_suit_pt}! Corte com {rank_display_pt} para levar esta vaza para sua aposta."
                elif lead_suit and rec_card.suit != lead_suit:
                    action_type = "slough"
                    tip_en = f"Void in {lead_suit}! Slough off {rank_display_en} safely."
                    tip_pt = f"Sem cartas de {lead_suit_pt}! Descarte {rank_display_pt} em segurança."
                elif int(rec_card) > int(current_highest):
                    action_type = "win"
                    tip_en = f"Play {rank_display_en} to capture this trick ({score_in_turn + 1}/{bet} needed)."
                    tip_pt = f"Jogue {rank_display_pt} para levar esta vaza ({score_in_turn + 1}/{bet} necessária(s))."
                else:
                    action_type = "duck"
                    tip_en = f"Hold your trump power: duck with {rank_display_en} under {current_highest}."
                    tip_pt = f"Poupe seus trunfos: passe com {rank_display_pt} abaixo de {current_highest_pt}."

        return {
            "recommended_card": card_str,
            "tip": tip_en,
            "tip_pt": tip_pt,
            "action_type": action_type,
            "needed_wins": needed_wins,
            "remaining_tricks": remaining_tricks,
        }
