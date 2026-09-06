from typing import List, Optional, Tuple, Dict
import random

from estimania.card import Card
from estimania.card_tracker import CardTracker

class CardPlayEngine:
    """
    Intelligent Grandmaster decision engine for trick play.
    Covers:
    - Contract fulfillment (target-based play)
    - Adversarial Opponent Sabotage:
        * Forcing unwanted tricks onto opponents who bid 0 or reached quota (especially the leader)
        * Starving opponents who need tricks to hit contracts
    - Ducking / underplaying when quota is met or bet was 0
    - Cashing winners / boss cards when tricks are needed
    - Strategic sloughing (dumping dangerous cards under opponent winners)
    - PIMC (Perfect Information Monte Carlo) forward rollout for high-leverage plays
    """

    def __init__(self, tracker: Optional[CardTracker] = None):
        self.tracker = tracker or CardTracker()
        # Sabotage weight: how heavily we penalize the leader's score relative to our own
        self.sabotage_weight = 0.75

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
        my_name: str = "Bot",
        active_player_names: Optional[List[str]] = None,
    ) -> Card:
        legal = self.get_legal_cards(hand, cards_in_table)
        if len(legal) == 1:
            return legal[0]

        needed_wins = bet - score_in_turn
        remaining_tricks = len(hand)
        is_leading = (len(cards_in_table) == 0)
        is_last_to_play = (len(cards_in_table) == total_players - 1)
        current_highest = max(cards_in_table, key=lambda c: int(c)) if not is_leading else None

        # Deep PIMC rollout lookahead for ALL hand sizes when multiple legal candidates exist
        if active_player_names and len(legal) > 1:
            best_card = self._evaluate_deep_pimc(
                legal=legal,
                hand=hand,
                cards_in_table=cards_in_table,
                bet=bet,
                score_in_turn=score_in_turn,
                total_players=total_players,
                my_name=my_name,
                active_player_names=active_player_names,
            )
            if best_card is not None:
                return best_card

        # 1. Quota reached or bet was 0 -> DO NOT WIN & SABOTAGE OPPONENTS!
        if needed_wins <= 0:
            return self._play_to_avoid_winning(
                legal, hand, cards_in_table, current_highest, is_last_to_play, my_name
            )

        # 2. Must win EVERY remaining trick -> WIN at all costs!
        if needed_wins >= remaining_tricks:
            return self._play_to_win_at_all_costs(
                legal, hand, cards_in_table, current_highest, is_last_to_play
            )

        # 3. Need some tricks (0 < needed_wins < remaining_tricks) -> Strategic balanced play
        return self._play_balanced(
            legal, hand, cards_in_table, current_highest, needed_wins, remaining_tricks, is_last_to_play, my_name
        )

    def _play_to_avoid_winning(
        self,
        legal: List[Card],
        hand: List[Card],
        cards_in_table: List[Card],
        current_highest: Optional[Card],
        is_last_to_play: bool,
        my_name: str,
    ) -> Card:
        """
        Goal: Strictly avoid taking the trick.
        When leading: find a suit to force an opponent who hates tricks or lead lowest.
        When following: play highest safe card to dump danger while staying under highest.
        """
        if not cards_in_table:
            # LEADING when we want 0 wins:
            # Sabotage check: can we lead a suit where an opponent who hates tricks (e.g. leader) must follow?
            leader_name = self.tracker.get_leader_name(my_name)
            if leader_name and self.tracker.does_opponent_hate_tricks(leader_name):
                # Check which suits the leader is NOT void in
                leader_voids = self.tracker.voids.get(leader_name, set())
                candidate_cards = [c for c in legal if c.suit not in leader_voids]
                if candidate_cards:
                    # Lead a low card in that suit to force the leader to take it!
                    return min(candidate_cards, key=lambda c: int(c))

            # Default: Lead lowest card in deck (lowest rank in lowest suit)
            return min(legal, key=lambda c: int(c))

        highest_val = int(current_highest)
        safe_cards = [c for c in legal if int(c) < highest_val]

        if safe_cards:
            lead_suit = cards_in_table[0].suit
            has_lead_suit = any(c.suit == lead_suit for c in legal)

            if has_lead_suit:
                # Following suit: play highest safe card to get rid of high cards without taking trick!
                return max(safe_cards, key=lambda c: int(c))
            else:
                # Void in lead suit: SLOUGH / DUMP our highest dangerous non-lead card!
                return max(safe_cards, key=lambda c: int(c))
        else:
            # Forced to exceed current highest
            if is_last_to_play:
                # No choice, we take the trick. Minimize card rank to save lower cards.
                return min(legal, key=lambda c: int(c))
            else:
                # Play highest to try to force remaining opponents to overtrump us
                return max(legal, key=lambda c: int(c))

    def _play_to_win_at_all_costs(
        self,
        legal: List[Card],
        hand: List[Card],
        cards_in_table: List[Card],
        current_highest: Optional[Card],
        is_last_to_play: bool,
    ) -> Card:
        """Goal: Must win this trick (needed_wins >= remaining_tricks)."""
        if not cards_in_table:
            # Lead highest boss card or highest card
            return max(legal, key=lambda c: int(c))

        highest_val = int(current_highest)
        winning_cards = [c for c in legal if int(c) > highest_val]

        if winning_cards:
            if is_last_to_play:
                # Last to act: win with the cheapest winning card to conserve high cards
                return min(winning_cards, key=lambda c: int(c))
            else:
                # Opponents still to act: play boss or highest winning card to prevent overtrumping
                bosses = [c for c in winning_cards if self.tracker.is_boss_card(c, hand)]
                if bosses:
                    return min(bosses, key=lambda c: int(c))
                return max(winning_cards, key=lambda c: int(c))
        else:
            # Cannot win: play lowest card
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
        my_name: str,
    ) -> Card:
        """Goal: Win exactly needed_wins of the remaining_tricks with sabotage awareness."""
        boss_cards = [c for c in hand if self.tracker.is_boss_card(c, hand)]
        boss_count = len(boss_cards)

        if not cards_in_table:
            # LEADING:
            # If boss cards exactly equal needed wins, cash one to secure it
            if boss_count >= needed_wins and boss_cards:
                legal_bosses = [c for c in legal if c in boss_cards]
                if legal_bosses:
                    return max(legal_bosses, key=lambda c: int(c))

            # Sabotage leader check:
            leader_name = self.tracker.get_leader_name(my_name)
            if leader_name and self.tracker.does_opponent_hate_tricks(leader_name):
                leader_voids = self.tracker.voids.get(leader_name, set())
                safe_lead_for_sabotage = [
                    c for c in legal if c.suit not in leader_voids and c not in boss_cards
                ]
                if safe_lead_for_sabotage:
                    return min(safe_lead_for_sabotage, key=lambda c: int(c))

            # Otherwise lead low from non-boss cards to develop voids or draw out opponent trumps
            non_bosses = [c for c in legal if c not in boss_cards]
            if non_bosses:
                return min(non_bosses, key=lambda c: int(c))
            return min(legal, key=lambda c: int(c))

        # NOT LEADING:
        highest_val = int(current_highest)
        winning_cards = [c for c in legal if int(c) > highest_val]
        safe_losing_cards = [c for c in legal if int(c) < highest_val]

        if is_last_to_play:
            # End of trick: exact control
            if winning_cards and (boss_count < needed_wins or not safe_losing_cards):
                return min(winning_cards, key=lambda c: int(c))
            elif safe_losing_cards:
                return max(safe_losing_cards, key=lambda c: int(c))
            else:
                return min(winning_cards, key=lambda c: int(c))

        # MIDDLE POSITION:
        if winning_cards and (boss_count < needed_wins):
            legal_bosses = [c for c in winning_cards if self.tracker.is_boss_card(c, hand)]
            if legal_bosses:
                return min(legal_bosses, key=lambda c: int(c))
            return max(winning_cards, key=lambda c: int(c))
        elif safe_losing_cards:
            return max(safe_losing_cards, key=lambda c: int(c))
        else:
            return min(legal, key=lambda c: int(c))

    def _evaluate_deep_pimc(
        self,
        legal: List[Card],
        hand: List[Card],
        cards_in_table: List[Card],
        bet: int,
        score_in_turn: int,
        total_players: int,
        my_name: str,
        active_player_names: List[str],
        num_samples: int = 30,
    ) -> Optional[Card]:
        """
        Ultra Grandmaster Deep PIMC Rollout:
        Sample unseen cards consistent with known voids, and simulate ALL remaining
        tricks to the end of the round with target-aware opponent play and sabotage.
        """
        other_names = [n for n in active_player_names if n != my_name]
        if not other_names:
            return None

        # Determine exact hand sizes for each opponent (opponents who already played this trick have len(hand) - 1)
        cards_played_so_far = len(cards_in_table)
        try:
            my_circular_idx = active_player_names.index(my_name)
        except ValueError:
            my_circular_idx = cards_played_so_far

        hand_sizes = {}
        for idx, name in enumerate(active_player_names):
            if name == my_name:
                continue
            if idx < my_circular_idx:
                hand_sizes[name] = max(0, len(hand) - 1)
            else:
                hand_sizes[name] = len(hand)

        scores_by_card: Dict[int, float] = {int(c): 0.0 for c in legal}
        samples_evaluated = 0

        # Adjust sample count dynamically based on hand size to ensure < 15ms latency
        actual_samples = min(num_samples, 40 if len(hand) <= 4 else 25)

        for _ in range(actual_samples):
            sampled_hands = self.tracker.sample_opponent_hands(
                opponent_names=other_names,
                hand_size=len(hand),
                my_hand=hand,
                hand_sizes=hand_sizes,
            )
            if not sampled_hands:
                continue

            samples_evaluated += 1

            for candidate_card in legal:
                # Simulate entire round starting from playing candidate_card
                sim_hands = {n: list(sampled_hands[n]) for n in other_names}
                sim_hands[my_name] = [c for c in hand if c != candidate_card]
                sim_wins = {n: self.tracker.opponent_wins.get(n, 0) for n in other_names}
                sim_wins[my_name] = score_in_turn

                # 1. Complete the current trick
                cur_trick_cards = list(cards_in_table) + [candidate_card]
                cur_trick_players = active_player_names[:my_circular_idx + 1]
                remaining_to_act = active_player_names[my_circular_idx + 1:]

                for i, opp_name in enumerate(remaining_to_act):
                    is_last = (i == len(remaining_to_act) - 1)
                    opp_h = sim_hands[opp_name]
                    if not opp_h:
                        continue
                    opp_bet = self.tracker.opponent_contracts.get(opp_name, 0)
                    wants = (opp_bet - sim_wins.get(opp_name, 0) > 0)
                    chosen = self._pick_rollout_card(opp_h, cur_trick_cards, wants, is_last)
                    opp_h.remove(chosen)
                    cur_trick_cards.append(chosen)
                    cur_trick_players.append(opp_name)

                # Who won current trick?
                highest_in_trick = max(cur_trick_cards, key=lambda c: int(c))
                win_player_idx = cur_trick_cards.index(highest_in_trick)
                trick_winner = cur_trick_players[win_player_idx]
                sim_wins[trick_winner] = sim_wins.get(trick_winner, 0) + 1

                # 2. Simulate all remaining tricks until hands are empty
                lead_player = trick_winner
                n_players = len(active_player_names)
                while len(sim_hands[my_name]) > 0:
                    try:
                        lead_idx = active_player_names.index(lead_player)
                    except ValueError:
                        lead_idx = 0
                    order = active_player_names[lead_idx:] + active_player_names[:lead_idx]
                    rem_trick_cards = []
                    rem_trick_players = []

                    for i, p_name in enumerate(order):
                        is_last = (i == n_players - 1)
                        p_h = sim_hands[p_name]
                        if not p_h:
                            continue
                        p_bet = self.tracker.opponent_contracts.get(p_name, 0) if p_name != my_name else bet
                        wants = (p_bet - sim_wins.get(p_name, 0) > 0)
                        chosen = self._pick_rollout_card(p_h, rem_trick_cards, wants, is_last)
                        p_h.remove(chosen)
                        rem_trick_cards.append(chosen)
                        rem_trick_players.append(p_name)

                    if rem_trick_cards:
                        highest_card = max(rem_trick_cards, key=lambda c: int(c))
                        win_pos = rem_trick_cards.index(highest_card)
                        lead_player = rem_trick_players[win_pos]
                        sim_wins[lead_player] = sim_wins.get(lead_player, 0) + 1
                    else:
                        break

                # 3. Score the full round outcome
                my_total = sim_wins.get(my_name, 0)
                if my_total == bet:
                    my_reward = 1.0 if bet == 0 else float(2 * bet)
                else:
                    my_reward = -float(abs(bet - my_total))

                # Opponent sabotage adjustment:
                leader_name = self.tracker.get_leader_name(my_name)
                if leader_name and leader_name in sim_wins:
                    l_bet = self.tracker.opponent_contracts.get(leader_name, 0)
                    l_wins = sim_wins[leader_name]
                    if l_wins == l_bet:
                        l_reward = 1.0 if l_bet == 0 else float(2 * l_bet)
                    else:
                        l_reward = -float(abs(l_bet - l_wins))
                    round_val = my_reward - (self.sabotage_weight * l_reward)
                else:
                    round_val = my_reward

                scores_by_card[int(candidate_card)] += round_val

        if samples_evaluated == 0:
            return None

        best_c_int = max(scores_by_card, key=scores_by_card.get)
        for c in legal:
            if int(c) == best_c_int:
                return c

        return None

    @staticmethod
    def _pick_rollout_card(hand: List[Card], trick: List[Card], wants_tricks: bool, is_last: bool) -> Card:
        """Heuristic rollout policy for fast multi-trick simulation."""
        if not trick:
            return max(hand, key=lambda c: int(c)) if wants_tricks else min(hand, key=lambda c: int(c))
        lead_suit = trick[0].suit
        legal = [c for c in hand if c.suit == lead_suit]
        if not legal:
            legal = hand
        cur_high = max(int(c) for c in trick)
        winners = [c for c in legal if int(c) > cur_high]
        losers = [c for c in legal if int(c) < cur_high]

        if wants_tricks:
            if winners:
                return min(winners, key=lambda c: int(c)) if is_last else max(winners, key=lambda c: int(c))
            return min(legal, key=lambda c: int(c))
        else:
            if losers:
                return max(losers, key=lambda c: int(c))
            return min(legal, key=lambda c: int(c)) if is_last else max(legal, key=lambda c: int(c))
