from typing import List, Dict, Any, Optional
import numpy as np
from estimania.card import Card

FEATURE_NAMES = [
    'n_cards',
    'n_adversaries',
    'position_ratio',
    'prior_bettors_count',
    'sum_prior_bets',
    'mean_prior_bets',
    'diamonds_count',
    'spades_count',
    'hearts_count',
    'clubs_count',
    'void_suits_count',
    'ace_diamonds',
    'ace_spades',
    'ace_hearts',
    'ace_clubs',
    'high_diamonds_count',
    'high_spades_count',
    'boss_tier_count',
    'upper_half_count',
    'duck_tier_count',
    'mean_card_val',
    'max_card_val',
    'min_card_val',
    'cand_bet',
    'bet_ratio',
    'oversubscribe_ratio',
]

def extract_hand_features(
    hand: List[Card],
    n_adversaries: int,
    current_bets: List[int],
    cand_bet: int,
) -> List[float]:
    """
    Extract a normalized, fixed-length feature vector representing a candidate bet
    for ANY hand size (1 to 13) and ANY number of players.
    """
    n_cards = len(hand)
    if n_cards == 0:
        return [0.0] * len(FEATURE_NAMES)

    card_vals = [int(c) for c in hand]
    
    # Prior bets analysis
    # current_bets contains bets placed by prior players, with unplaced bets as -1
    valid_prior_bets = [b for b in current_bets if b >= 0]
    prior_bettors_count = len(valid_prior_bets)
    total_players = n_adversaries + 1
    position_ratio = prior_bettors_count / max(1, total_players)
    sum_prior_bets = sum(valid_prior_bets)
    mean_prior_bets = (sum_prior_bets / prior_bettors_count) if prior_bettors_count > 0 else 0.0

    # Suits breakdown
    diamonds = [c for c in hand if c.suit == 'Diamonds']
    spades = [c for c in hand if c.suit == 'Spades']
    hearts = [c for c in hand if c.suit == 'Hearts']
    clubs = [c for c in hand if c.suit == 'Clubs']

    void_suits_count = sum(1 for suit_cards in [diamonds, spades, hearts, clubs] if len(suit_cards) == 0)

    # Aces (int values: Clubs Ace = 13, Hearts Ace = 26, Spades Ace = 39, Diamonds Ace = 52)
    ace_diamonds = 1.0 if any(int(c) == 52 for c in hand) else 0.0
    ace_spades = 1.0 if any(int(c) == 39 for c in hand) else 0.0
    ace_hearts = 1.0 if any(int(c) == 26 for c in hand) else 0.0
    ace_clubs = 1.0 if any(int(c) == 13 for c in hand) else 0.0

    # High cards: Diamonds 10..Ace are values 48..52; Spades 10..Ace are values 35..39
    high_diamonds_count = sum(1 for c in diamonds if int(c) >= 48)
    high_spades_count = sum(1 for c in spades if int(c) >= 35)

    # Tiers
    boss_tier_count = sum(1 for v in card_vals if v >= 40)      # High diamonds & top trumps
    upper_half_count = sum(1 for v in card_vals if v >= 26)     # Spades & Diamonds
    duck_tier_count = sum(1 for v in card_vals if v <= 14)      # Low clubs/hearts

    mean_card_val = float(np.mean(card_vals)) / 52.0
    max_card_val = float(np.max(card_vals)) / 52.0
    min_card_val = float(np.min(card_vals)) / 52.0

    bet_ratio = float(cand_bet) / max(1, n_cards)
    oversubscribe_ratio = float(sum_prior_bets + cand_bet) / max(1, n_cards)

    return [
        float(n_cards),
        float(n_adversaries),
        float(position_ratio),
        float(prior_bettors_count),
        float(sum_prior_bets),
        float(mean_prior_bets),
        float(len(diamonds)),
        float(len(spades)),
        float(len(hearts)),
        float(len(clubs)),
        float(void_suits_count),
        ace_diamonds,
        ace_spades,
        ace_hearts,
        ace_clubs,
        float(high_diamonds_count),
        float(high_spades_count),
        float(boss_tier_count),
        float(upper_half_count),
        float(duck_tier_count),
        mean_card_val,
        max_card_val,
        min_card_val,
        float(cand_bet),
        bet_ratio,
        oversubscribe_ratio,
    ]
