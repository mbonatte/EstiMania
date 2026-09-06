from typing import List, Optional, Tuple, Dict
import random

from estimania.card import Card
from estimania.card_tracker import CardTracker

class CardPlayEngine:
    """
    Intelligent decision engine for selecting cards during trick play.
    Covers:
    - Contract fulfillment (target-based play)
    - Ducking / underplaying when quota is met or bet is 0
    - Cashing winners / boss cards when tricks are needed
    - Strategic sloughing (dumping dangerous cards under opponent winners)
    - Forcing opponents who want to avoid tricks to take them
    - Rollout evaluation (PIMC) for tight/ambiguous decisions
    """

    def __init__(self, tracker: Optional[CardTracker] = None):
        self.tracker = tracker or CardTracker()

    def get_legal_cards(self, hand: List[Card], cards_in_table: List[Card]) -> List[Card]:
        """Filter hand for cards that follow suit, or all cards if void in lead suit."""
        if not cards_in_table:
            return list(hand)
        lead_suit = cards_in_table[0].suit
        matching = [c for c in hand if c.suit == lead_suit]
        return matching if matching else list(hand)

    def select_card(
        self,
        hand: List[Card],
        cards_in_table: List[Card],
        bet: int,
        score_in_turn: int,
        total_players: int = 4,
        opponent_bets: Optional[List[int]] = None,
        opponent_wins: Optional[List[int]] = None,
    ) -> Card:
        """
        Choose the best card to play given the game state.
        """
        legal = self.get_legal_cards(hand, cards_in_table)
        if len(legal) == 1:
            return legal[0]

        needed_wins = bet - score_in_turn
        remaining_tricks = len(hand)
        is_leading = (len(cards_in_table) == 0)
        is_last_to_play = (len(cards_in_table) == total_players - 1)

        # Current highest card on table if not leading
        current_highest = max(cards_in_table, key=lambda c: int(c)) if not is_leading else None

        # Case 1: Quota reached or bet was 0 -> Absolutely DO NOT win!
        if needed_wins <= 0:
            return self._play_to_avoid_winning(legal, hand, cards_in_table, current_highest, is_last_to_play)

        # Case 2: Must win EVERY remaining trick -> WIN at all costs!
        if needed_wins >= remaining_tricks:
            return self._play_to_win_at_all_costs(legal, hand, cards_in_table, current_highest, is_last_to_play)

        # Case 3: Need some tricks (0 < needed_wins < remaining_tricks) -> Strategic balanced play
        return self._play_balanced(
            legal, hand, cards_in_table, current_highest, needed_wins, remaining_tricks, is_last_to_play
        )

    def _play_to_avoid_winning(
        self,
        legal: List[Card],
        hand: List[Card],
        cards_in_table: List[Card],
        current_highest: Optional[Card],
        is_last_to_play: bool,
    ) -> Card:
        """
        Goal: Avoid winning the trick. If unavoidable, minimize future damage.
        """
        if not cards_in_table:
            # LEADING when we want 0 wins:
            # Lead our lowest card in the lowest suit (Clubs/Hearts), keeping high cards away from the lead
            # Sort ascending by int(c)
            sorted_legal = sorted(legal, key=lambda c: int(c))
            return sorted_legal[0]

        # NOT LEADING:
        # Safe cards are those that are strictly lower than the current highest on the table
        highest_val = int(current_highest)
        safe_cards = [c for c in legal if int(c) < highest_val]

        if safe_cards:
            # We have safe cards that cannot take the trick!
            lead_suit = cards_in_table[0].suit
            has_lead_suit = any(c.suit == lead_suit for c in legal)

            if has_lead_suit:
                # Following suit: play the highest safe card in suit!
                # Dumping higher cards while staying safe preserves ultra-low cards for future tricks.
                return max(safe_cards, key=lambda c: int(c))
            else:
                # Void in lead suit: SLOUGHING / DUMPING!
                # We can safely discard a high card (e.g. high Heart or high Spade that is < highest_val)
                # without winning! This is great because it gets rid of potential accidental winners.
                return max(safe_cards, key=lambda c: int(c))
        else:
            # Unfortunate: ALL legal cards are higher than the current highest on the table!
            # If we are not last to play, playing our highest might trigger someone else to beat us,
            # or playing our lowest minimizes high card loss.
            # Usually playing the lowest card is best to conserve our hand or minimize overshoot.
            return min(legal, key=lambda c: int(c))

    def _play_to_win_at_all_costs(
        self,
        legal: List[Card],
        hand: List[Card],
        cards_in_table: List[Card],
        current_highest: Optional[Card],
        is_last_to_play: bool,
    ) -> Card:
        """
        Goal: Must win this trick (needed_wins >= remaining_tricks).
        """
        if not cards_in_table:
            # Leading: play our highest boss card or highest overall card to guarantee the trick
            return max(legal, key=lambda c: int(c))

        highest_val = int(current_highest)
        winning_cards = [c for c in legal if int(c) > highest_val]

        if winning_cards:
            if is_last_to_play:
                # Last to act: play the MINIMUM winning card to conserve higher winners for future tricks
                return min(winning_cards, key=lambda c: int(c))
            else:
                # Opponents still to act: play our highest winning card (or boss card) to resist overtrumping
                bosses = [c for c in winning_cards if self.tracker.is_boss_card(c, hand)]
                if bosses:
                    return min(bosses, key=lambda c: int(c))
                return max(winning_cards, key=lambda c: int(c))
        else:
            # Cannot win this trick: play our lowest card to save high cards for the tricks we can win
            return min(legal, key=lambda c: int(c))

    def _play_balanced(
        self,
        legal: List[Card],
        hand: List[Card],
        cards_in_table: List[Card],
        current_highest: Optional[Card],
        needed_wins: int,
        remaining_tricks: int,
        is_last_to_play: bool,
    ) -> Card:
        """
        Goal: Win exactly needed_wins of the remaining_tricks.
        """
        # Count boss cards or near-boss cards in the entire hand
        boss_cards = [c for c in hand if self.tracker.is_boss_card(c, hand)]
        boss_count = len(boss_cards)

        if not cards_in_table:
            # LEADING:
            # If we already have enough boss cards to cover our needed wins, cash one or lead safe
            if boss_count >= needed_wins and boss_cards:
                # Cash a boss card now to lock in a win
                legal_bosses = [c for c in legal if c in boss_cards]
                if legal_bosses:
                    return max(legal_bosses, key=lambda c: int(c))
            # Otherwise, lead low in our shortest or longest suit to develop voids or draw out trumps
            # Leading low from non-boss cards:
            non_bosses = [c for c in legal if c not in boss_cards]
            if non_bosses:
                return min(non_bosses, key=lambda c: int(c))
            return min(legal, key=lambda c: int(c))

        # NOT LEADING:
        highest_val = int(current_highest)
        winning_cards = [c for c in legal if int(c) > highest_val]
        safe_losing_cards = [c for c in legal if int(c) < highest_val]

        if is_last_to_play:
            # PERFECT INFORMATION at end of trick!
            # We can either win (if winning_cards exist) or duck (if safe_losing_cards exist).
            if winning_cards and (boss_count < needed_wins or not safe_losing_cards):
                # We need wins! Take the trick with the cheapest winning card!
                return min(winning_cards, key=lambda c: int(c))
            elif safe_losing_cards:
                # We have enough future winners or prefer to duck: duck with highest safe card!
                return max(safe_losing_cards, key=lambda c: int(c))
            else:
                # Forced to win
                return min(winning_cards, key=lambda c: int(c))

        # MIDDLE POSITION (opponents still to act after us):
        if winning_cards and (boss_count < needed_wins):
            # Try to win: if we have a boss card, cash it; otherwise play high winner
            legal_bosses = [c for c in winning_cards if self.tracker.is_boss_card(c, hand)]
            if legal_bosses:
                return min(legal_bosses, key=lambda c: int(c))
            return max(winning_cards, key=lambda c: int(c))
        elif safe_losing_cards:
            # Duck: play highest safe card
            return max(safe_losing_cards, key=lambda c: int(c))
        else:
            return min(legal, key=lambda c: int(c))
