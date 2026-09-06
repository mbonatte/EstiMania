import random
from typing import List, Dict, Tuple
from estimania.deck import Deck
from estimania.card import Card
from estimania.game_rules import GameRules
from estimania.card_play_engine import CardPlayEngine
from estimania.card_tracker import CardTracker
from estimania.features import extract_hand_features

def compute_reward(bet: int, actual_wins: int) -> float:
    """Compute score/reward according to EstiMania rules."""
    if bet == actual_wins:
        return 1.0 if bet == 0 else float(2 * bet)
    return -float(abs(bet - actual_wins))

class SimPlayer:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.bet: int = -1
        self.score_in_turn: int = 0
        self.score: int = 0
        self.tracker = CardTracker()
        self.play_engine = CardPlayEngine(self.tracker)

    def is_moviment_valid(self, card_selected: Card, cards_in_table: List[Card]) -> bool:
        if len(cards_in_table) == 0:
            return True
        first_card = cards_in_table[0]
        if card_selected.suit == first_card.suit:
            return True
        for card in self.hand:
            if card.suit == first_card.suit:
                return False
        return True

    def select_card(self, cards_in_table: List[Card], total_players: int, active_names: List[str]) -> Card:
        card = self.play_engine.select_card(
            hand=self.hand,
            cards_in_table=cards_in_table,
            bet=self.bet,
            score_in_turn=self.score_in_turn,
            total_players=total_players,
            my_name=self.name,
            active_player_names=active_names,
        )
        self.hand.remove(card)
        return card

def estimate_hand_heuristic_wins(hand: List[Card], n_players: int) -> int:
    """Fast heuristic estimate of how many tricks a hand can win."""
    wins = 0.0
    for c in hand:
        val = int(c)
        if val == 52:
            wins += 0.95
        elif val >= 48:
            wins += 0.80
        elif val >= 40:
            wins += 0.55
        elif val == 39:
            wins += 0.70
        elif val >= 35:
            wins += 0.50
        elif val == 26:
            wins += 0.40
        elif val == 13:
            wins += 0.25
        else:
            wins += 0.05
    return int(round(wins))

def simulate_single_round(
    num_players: int,
    n_cards: int,
    bet_policy_model=None,
) -> List[Tuple[List[float], float]]:
    """
    Simulate one round of n_cards with num_players using Grandmaster play engines.
    Returns list of (feature_vector, actual_reward) training samples.
    """
    players = [SimPlayer(f"P{i}") for i in range(num_players)]
    rules = GameRules()

    # Deal cards
    deck = Deck()
    for p in players:
        p.hand = sorted(deck.deal(n_cards), reverse=True)
        p.tracker.reset_round()
        p.tracker.register_my_hand(p.hand)
        p.score_in_turn = 0

    # Collect bets sequentially
    current_bets = [-1] * num_players
    contracts_dict = {}
    hand_snapshots = {i: list(players[i].hand) for i in range(num_players)}

    for i, p in enumerate(players):
        if bet_policy_model is not None:
            best_b = 0
            best_pred = float('-inf')
            for cand_b in range(n_cards + 1):
                feats = extract_hand_features(p.hand, num_players - 1, current_bets, cand_b)
                pred = bet_policy_model.predict([feats])[0]
                if pred > best_pred:
                    best_pred = pred
                    best_b = cand_b
            p.bet = best_b
        else:
            est = estimate_hand_heuristic_wins(p.hand, num_players)
            p.bet = min(n_cards, max(0, est))

        current_bets[i] = p.bet
        contracts_dict[p.name] = p.bet

    # Broadcast contracts to all trackers for adversarial sabotage
    for p in players:
        p.tracker.set_opponent_contracts(contracts_dict)

    # Play tricks
    lead_player_idx = 0
    for _ in range(n_cards):
        trick_order = players[lead_player_idx:] + players[:lead_player_idx]
        cards_in_table = []
        active_names = [p.name for p in trick_order]

        for p in trick_order:
            card = p.select_card(cards_in_table, total_players=num_players, active_names=active_names)
            cards_in_table.append(card)

        # Notify trackers
        lead_suit = cards_in_table[0].suit
        for p_who_played, card_played in zip(trick_order, cards_in_table):
            for observer in players:
                observer.tracker.record_trick_card(p_who_played.name, card_played, lead_suit)

        # Evaluate trick winner
        winner_offset, highest_card = rules.evaluate_trick_winner(cards_in_table, lead_player_idx)
        winner = players[winner_offset]
        winner.score_in_turn += 1
        for observer in players:
            observer.tracker.record_trick_winner(winner.name)
        lead_player_idx = winner_offset

    # Generate training records
    training_samples = []
    prior_bets_tracker = [-1] * num_players

    for i in range(num_players):
        actual_wins = players[i].score_in_turn
        hand = hand_snapshots[i]

        for cand_b in range(n_cards + 1):
            reward = compute_reward(cand_b, actual_wins)
            feats = extract_hand_features(hand, num_players - 1, prior_bets_tracker, cand_b)
            training_samples.append((feats, reward))

        prior_bets_tracker[i] = players[i].bet

    return training_samples
