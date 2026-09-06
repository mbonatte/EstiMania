from typing import List, Optional, Dict
from estimania.card import Card
from estimania.deck import Deck
from estimania.card_tracker import CardTracker

class FinalRoundAI:
    """
    Game-theoretic solver for the Final Round ('Blind Man's Bluff'):
    - Each player holds 1 card face down (unseen to them, seen by all others).
    - Calculates exact win probability P(win) over unseen deck.
    - Performs Bayesian belief updating on own card based on opponents' prior bets.
    - Incorporates strategic bluffing and score-dependent risk taking.
    """

    def __init__(self, tracker: Optional[CardTracker] = None):
        self.tracker = tracker or CardTracker()
        self.full_deck = Deck().deck

    def compute_prior_win_probability(
        self,
        opponent_cards: List[Card],
        unseen_cards: Optional[List[Card]] = None,
    ) -> float:
        """
        Calculate prior probability that bot's card is higher than all opponents' cards.
        """
        if not opponent_cards:
            return 0.5

        if unseen_cards is None:
            # All cards in 52 deck except opponent cards
            opp_ints = set(int(c) for c in opponent_cards)
            unseen_cards = [c for c in self.full_deck if int(c) not in opp_ints]

        if not unseen_cards:
            return 0.0

        max_opp_val = max(int(c) for c in opponent_cards)
        winning_cards_count = sum(1 for c in unseen_cards if int(c) > max_opp_val)

        return winning_cards_count / len(unseen_cards)

    def bayesian_posterior_win_probability(
        self,
        opponent_cards: List[Card],
        prior_bets_made: List[int],
        unseen_cards: Optional[List[Card]] = None,
    ) -> float:
        """
        Update win probability using Bayesian inference from prior bets made by opponents who saw bot's card.
        """
        if not opponent_cards:
            return 0.5

        opp_ints = set(int(c) for c in opponent_cards)
        if unseen_cards is None:
            unseen_cards = [c for c in self.full_deck if int(c) not in opp_ints]

        if not unseen_cards:
            return 0.0

        max_opp_val = max(int(c) for c in opponent_cards)

        # Filter out invalid / unplaced bets (-1)
        valid_prior_bets = [b for b in prior_bets_made if b >= 0]

        if not valid_prior_bets:
            # No prior bets made yet -> return prior probability
            winning_count = sum(1 for c in unseen_cards if int(c) > max_opp_val)
            return winning_count / len(unseen_cards)

        # Bayesian likelihood weighting over each candidate card c in unseen_cards
        # For an opponent k who saw c:
        # If opponent k bet 1, it's more likely that c is beatable (i.e. int(c) is not 52).
        weights = []
        for cand in unseen_cards:
            cand_val = int(cand)
            likelihood = 1.0

            for bet in valid_prior_bets:
                # If opponent bet 1:
                # Approximate probability opponent bet 1 given candidate card value
                # Opponents are less likely to bet 1 if cand_val is very high (e.g. 52 Ace of Diamonds)
                if bet == 1:
                    # Likelihood of betting 1 decreases as cand_val approaches 52
                    p_bet_1 = max(0.05, 1.0 - (cand_val / 53.0))
                    likelihood *= p_bet_1
                elif bet == 0:
                    # Opponents more likely to bet 0 if cand_val is high
                    p_bet_0 = min(0.95, 0.2 + 0.8 * (cand_val / 53.0))
                    likelihood *= p_bet_0

            weights.append(likelihood)

        total_weight = sum(weights)
        if total_weight <= 1e-9:
            winning_count = sum(1 for c in unseen_cards if int(c) > max_opp_val)
            return winning_count / len(unseen_cards)

        # Posterior probability that cand_val > max_opp_val
        weighted_win_prob = sum(
            weights[i] for i, cand in enumerate(unseen_cards) if int(cand) > max_opp_val
        ) / total_weight

        return weighted_win_prob

    def decide_bet(
        self,
        opponent_cards: List[Card],
        prior_bets_made: List[int],
        my_score: int = 0,
        leader_score: int = 0,
        bluff_tendency: float = 0.15,
    ) -> int:
        """
        Decide whether to bet 1 or 0 in the final round.
        Threshold:
        E[bet 1] = 3P - 1
        E[bet 0] = 1 - 2P
        3P - 1 > 1 - 2P <=> P > 0.40.
        """
        p_win = self.bayesian_posterior_win_probability(opponent_cards, prior_bets_made)

        # If behind in score, lower threshold to take calculated risks for comeback
        score_deficit = leader_score - my_score
        threshold = 0.40
        if score_deficit > 0:
            # Need to gamble to catch up
            threshold = max(0.28, 0.40 - 0.03 * min(score_deficit, 4))

        # Strategic bluffing: if betting early and close to threshold, occasionally bluff 1
        is_early_bettor = (len([b for b in prior_bets_made if b >= 0]) == 0)
        if is_early_bettor and (threshold - 0.06 <= p_win < threshold):
            import random
            if random.random() < bluff_tendency:
                return 1

        return 1 if p_win >= threshold else 0
