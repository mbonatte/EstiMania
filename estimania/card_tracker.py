from typing import List, Set, Dict, Optional
from estimania.card import Card
from estimania.deck import Deck

class CardTracker:
    """
    Tracks state and card information throughout games and rounds:
    - Played cards across tricks and rounds.
    - Unseen cards in the deck / opponent hands.
    - Opponent suit voids (when a player fails to follow suit).
    - Boss card calculation (cards that cannot be beaten by any remaining unseen card).
    """

    ALL_SUITS = ['Diamonds', 'Spades', 'Hearts', 'Clubs']

    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Reset the tracker for a completely new game."""
        self.full_deck = Deck().deck
        self.seen_in_game: Set[int] = set()
        self.reset_round()

    def reset_round(self):
        """Reset information specific to a single round."""
        self.played_in_round: List[Card] = []
        self.voids: Dict[str, Set[str]] = {}
        self.lead_suit: Optional[str] = None

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
        Because in EstiMania int(c1) > int(c2) <=> c1 > c2 (Diamonds > Spades > Hearts > Clubs, Ace high),
        a card is boss if there is no remaining unseen card with int(other) > int(card).
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
