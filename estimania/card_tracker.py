from typing import List, Set, Dict, Optional, Tuple
import random
from estimania.card import Card
from estimania.deck import Deck

class CardTracker:
    """
    Tracks state, cards, and opponent contracts throughout games and rounds:
    - Played cards across tricks and rounds.
    - Unseen cards in the deck / opponent hands.
    - Opponent suit voids (when a player fails to follow suit).
    - Boss card calculation.
    - Opponent contracts, trick wins, and game match leader tracking.
    - Sampling opponent hands consistent with voids for PIMC search.
    """

    ALL_SUITS = ['Diamonds', 'Spades', 'Hearts', 'Clubs']

    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Reset the tracker for a completely new game."""
        self.full_deck = Deck().deck
        self.seen_in_game: Set[int] = set()
        self.match_scores: Dict[str, int] = {}
        self.reset_round()

    def reset_round(self):
        """Reset information specific to a single round."""
        self.played_in_round: List[Card] = []
        self.voids: Dict[str, Set[str]] = {}
        self.lead_suit: Optional[str] = None
        self.opponent_contracts: Dict[str, int] = {}
        self.opponent_wins: Dict[str, int] = {}

    def set_match_scores(self, scores: Dict[str, int]):
        """Update cumulative scores across rounds."""
        self.match_scores = dict(scores)

    def set_opponent_contracts(self, contracts: Dict[str, int]):
        """Set all players' bids for the current round."""
        self.opponent_contracts = dict(contracts)
        for p in contracts:
            if p not in self.opponent_wins:
                self.opponent_wins[p] = 0

    def record_trick_winner(self, winner_name: str):
        """Record who took the trick."""
        if winner_name in self.opponent_wins:
            self.opponent_wins[winner_name] += 1
        else:
            self.opponent_wins[winner_name] = 1

    def get_leader_name(self, my_name: str) -> Optional[str]:
        """Find the opponent currently in the lead (highest cumulative match score)."""
        other_scores = {p: s for p, s in self.match_scores.items() if p != my_name}
        if not other_scores:
            return None
        return max(other_scores, key=other_scores.get)

    def get_opponent_needed_wins(self, player_name: str) -> int:
        """How many more tricks does this player need to make their contract?"""
        bet = self.opponent_contracts.get(player_name, 0)
        wins = self.opponent_wins.get(player_name, 0)
        return bet - wins

    def does_opponent_hate_tricks(self, player_name: str) -> bool:
        """True if the opponent has already hit their contract or bid 0 (further tricks will bust them)."""
        needed = self.get_opponent_needed_wins(player_name)
        return needed <= 0

    def register_my_hand(self, hand: List[Card]):
        """Record the player's own hand as seen."""
        for c in hand:
            self.seen_in_game.add(int(c))

    def record_trick_card(self, player_name: str, card: Card, lead_suit: Optional[str]):
        """Record a card played in a trick and detect if player showed void in lead suit."""
        self.seen_in_game.add(int(card))
        self.played_in_round.append(card)

        if lead_suit is not None and card.suit != lead_suit:
            if player_name not in self.voids:
                self.voids[player_name] = set()
            self.voids[player_name].add(lead_suit)

    def get_unseen_cards(self, my_hand: List[Card]) -> List[Card]:
        """Return all cards in the deck that are not in my hand and have not been seen in the round."""
        known_ints = set(int(c) for c in my_hand) | set(int(c) for c in self.played_in_round)
        return [c for c in self.full_deck if int(c) not in known_ints]

    def is_boss_card(self, card: Card, my_hand: List[Card]) -> bool:
        """
        Check if no unseen card in opponents' hands can beat this card.
        In EstiMania int(c1) > int(c2) <=> c1 > c2 (Diamonds > Spades > Hearts > Clubs, Ace high).
        """
        card_val = int(card)
        known_ints = set(int(c) for c in my_hand) | set(int(c) for c in self.played_in_round)
        for c in self.full_deck:
            val = int(c)
            if val > card_val and val not in known_ints:
                return False
        return True

    def count_higher_unseen(self, card: Card, my_hand: List[Card]) -> int:
        """Count how many unseen cards are strictly higher than this card."""
        card_val = int(card)
        known_ints = set(int(c) for c in my_hand) | set(int(c) for c in self.played_in_round)
        count = 0
        for c in self.full_deck:
            val = int(c)
            if val > card_val and val not in known_ints:
                count += 1
        return count

    def sample_opponent_hands(
        self,
        opponent_names: List[str],
        hand_size: int,
        my_hand: List[Card],
    ) -> Optional[Dict[str, List[Card]]]:
        """
        Sample a plausible distribution of remaining cards to opponents,
        strictly respecting known void constraints for each opponent.
        Used by Perfect Information Monte Carlo (PIMC).
        """
        unseen = self.get_unseen_cards(my_hand)
        total_needed = len(opponent_names) * hand_size
        if len(unseen) < total_needed:
            return None

        # Try up to 8 randomized partition attempts
        for _ in range(8):
            shuffled = list(unseen)
            random.shuffle(shuffled)
            assigned: Dict[str, List[Card]] = {name: [] for name in opponent_names}
            pool = list(shuffled)
            success = True

            for name in opponent_names:
                void_suits = self.voids.get(name, set())
                valid_for_player = [c for c in pool if c.suit not in void_suits]
                if len(valid_for_player) < hand_size:
                    success = False
                    break
                selected = valid_for_player[:hand_size]
                assigned[name] = selected
                for c in selected:
                    pool.remove(c)

            if success:
                return assigned

        # Fallback: ignore voids if constraint is too tight
        shuffled = list(unseen)
        random.shuffle(shuffled)
        assigned = {}
        for idx, name in enumerate(opponent_names):
            assigned[name] = shuffled[idx * hand_size : (idx + 1) * hand_size]
        return assigned
