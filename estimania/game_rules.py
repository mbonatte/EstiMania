from typing import List, Tuple, Dict
from .deck import Deck

class GameRules:
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns

    def build_match_sequence(self, num_players: int) -> List[int]:
        """Return the number of cards per round (e.g., 1..N..1) bounded by max_turns and deck size."""
        n = min(52 // num_players, self.max_turns)
        return [i + 1 for i in range(n)] + list(range(n, 0, -1))
    
    def deal(self, players, n_cards: int) -> None:
        """Deal n_cards to each player and sort hands high-to-low."""
        deck = Deck()
        for p in players:
            p.hand = sorted(deck.deal(n_cards), reverse=True)

    def evaluate_trick_winner(
        self, cards_in_table: List, starting_index_player: int = 0
    ) -> Tuple[int, object]:
        """
        Compute which offset (0-based in the rotated order) won the trick.
        Returns (winner_offset, highest_card).
        The caller maps offset back to absolute player index.
        """
        n_cards = len(cards_in_table)
        # Rotate the list so index 0 is the leader
        rotated = (cards_in_table[n_cards - starting_index_player:] 
                   + cards_in_table[:n_cards - starting_index_player])
        highest_card = rotated[0]
        winner_offset = 0
        for i, card in enumerate(rotated):
            if card > highest_card:
                winner_offset, highest_card = i, card
        return winner_offset, highest_card