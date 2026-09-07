import os
import random
import copy
import time
import pickle
from typing import List, Dict, Tuple
import numpy as np

from estimania.deck import Deck
from estimania.card import Card
from estimania.game_rules import GameRules
from estimania.card_tracker import CardTracker
from estimania.card_play_engine import CardPlayEngine

# Genome parameter names and search bounds
PARAM_SPECS = {
    'diamond_weight': (0.8, 1.5),
    'spade_weight': (0.5, 1.2),
    'heart_weight': (0.3, 0.9),
    'club_weight': (0.1, 0.6),
    'ace_bonus': (0.4, 1.4),
    'king_queen_bonus': (0.2, 0.9),
    'short_suit_bonus': (0.0, 0.8),
    'zero_bid_safety_margin': (0.1, 0.9),
    'sabotage_weight': (0.2, 1.2),
    'catchup_aggression': (0.0, 1.0),
}

PARAM_KEYS = list(PARAM_SPECS.keys())

def random_genome() -> Dict[str, float]:
    return {k: random.uniform(low, high) for k, (low, high) in PARAM_SPECS.items()}

def clamp_genome(genome: Dict[str, float]) -> Dict[str, float]:
    clamped = {}
    for k, (low, high) in PARAM_SPECS.items():
        clamped[k] = max(low, min(high, genome.get(k, (low + high) / 2)))
    return clamped

class GABot:
    """A bot configured with genome weights for bidding & play."""
    def __init__(self, name: str, genome: Dict[str, float]):
        self.name = name
        self.genome = genome
        self.hand: List[Card] = []
        self.bet = 0
        self.score_in_turn = 0
        self.score = 0
        self.tracker = CardTracker()
        self.play_engine = CardPlayEngine(self.tracker)
        self.play_engine.sabotage_weight = genome.get('sabotage_weight', 0.75)

    def evaluate_bidding(self, n_adversaries: int, current_bets: List[int], leader_score: int) -> int:
        n_cards = len(self.hand)
        if n_cards == 0:
            return 0

        # Weighted card evaluation
        suit_weights = {
            'Diamonds': self.genome['diamond_weight'],
            'Spades': self.genome['spade_weight'],
            'Hearts': self.genome['heart_weight'],
            'Clubs': self.genome['club_weight'],
        }

        est_tricks = 0.0
        suit_counts = {'Diamonds': 0, 'Spades': 0, 'Hearts': 0, 'Clubs': 0}

        for c in self.hand:
            suit_counts[c.suit] += 1
            sw = suit_weights.get(c.suit, 0.5)
            rank = int(c.value)  # 1..13

            # Rank evaluation
            if rank == 1:  # Ace
                est_tricks += 0.85 * sw * self.genome['ace_bonus']
            elif rank in [13, 12]:  # King, Queen
                est_tricks += 0.60 * sw * self.genome['king_queen_bonus']
            elif rank >= 9:
                est_tricks += 0.35 * sw
            else:
                est_tricks += 0.05 * sw

        # Short suit / void advantage
        voids_or_singletons = sum(1 for cnt in suit_counts.values() if cnt <= 1)
        est_tricks += voids_or_singletons * self.genome['short_suit_bonus'] * 0.15

        # Catchup bonus if behind the leader
        deficit = leader_score - self.score
        if deficit > 3 and n_cards >= 3:
            est_tricks += self.genome['catchup_aggression'] * 0.4

        # Zero bid threshold
        raw_bet = int(round(est_tricks))
        if est_tricks < self.genome['zero_bid_safety_margin']:
            raw_bet = 0

        return min(n_cards, max(0, raw_bet))

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

from multiprocessing import Pool

def play_match(
    genome: Dict[str, float],
    num_turns: int = 4,
    champion_genome: Dict[str, float] = None,
    num_players: int = 5,
) -> int:
    """Play a complete match against diverse baseline opponents and return points scored."""
    rules = GameRules()
    player_ga = GABot("GABot", genome)
    
    # Diverse baseline opponents
    default_g = {k: (low + high) / 2 for k, (low, high) in PARAM_SPECS.items()}
    p_heuristic = GABot("Heuristic", default_g)
    
    aggressive_g = dict(default_g)
    aggressive_g['ace_bonus'] = 1.3
    p_aggressive = GABot("Aggressive", aggressive_g)

    cautious_g = dict(default_g)
    cautious_g['zero_bid_safety_margin'] = 0.8
    p_cautious = GABot("Cautious", cautious_g)

    p_champ = GABot("PastChampion", champion_genome) if champion_genome else GABot("Heuristic2", default_g)

    if num_players == 5:
        players = [player_ga, p_heuristic, p_aggressive, p_cautious, p_champ]
    elif num_players == 3:
        players = [player_ga, p_heuristic, p_champ]
    elif num_players == 2:
        players = [player_ga, p_champ]
    else:
        players = [player_ga, p_heuristic, p_aggressive, p_champ]

    total_players = len(players)

    for turn_idx in range(1, num_turns + 1):
        n_cards = turn_idx
        deck = Deck()
        for p in players:
            p.hand = sorted(deck.deal(n_cards), reverse=True)
            p.tracker.reset_round()
            p.tracker.register_my_hand(p.hand)
            p.score_in_turn = 0

        # Highest score leader
        leader_score = max(p.score for p in players)

        # Collect bets
        current_bets = []
        contracts_dict = {}
        for p in players:
            b = p.evaluate_bidding(total_players - 1, current_bets, leader_score)
            p.bet = b
            current_bets.append(b)
            contracts_dict[p.name] = b

        for p in players:
            p.tracker.set_opponent_contracts(contracts_dict)

        # Play tricks
        lead_idx = turn_idx % total_players
        for _ in range(n_cards):
            trick_order = players[lead_idx:] + players[:lead_idx]
            cards_in_table = []
            active_names = [p.name for p in trick_order]

            for p in trick_order:
                c = p.select_card(cards_in_table, total_players, active_names)
                cards_in_table.append(c)

            lead_suit = cards_in_table[0].suit
            for p_played, c_played in zip(trick_order, cards_in_table):
                for obs in players:
                    obs.tracker.record_trick_card(p_played.name, c_played, lead_suit)

            winner_offset, _ = rules.evaluate_trick_winner(cards_in_table, lead_idx)
            winner = players[winner_offset]
            winner.score_in_turn += 1
            for obs in players:
                obs.tracker.record_trick_winner(winner.name)
            lead_idx = winner_offset

        # End of turn scoring
        for p in players:
            if p.bet == p.score_in_turn:
                pts = 1 if p.bet == 0 else 2 * p.bet
            else:
                pts = -abs(p.bet - p.score_in_turn)
            p.score += pts

    return player_ga.score

def _eval_individual_worker(args) -> float:
    genome, matches_per_eval, champion_genome, num_players = args
    scores = [
        play_match(genome, num_turns=4, champion_genome=champion_genome, num_players=num_players)
        for _ in range(matches_per_eval)
    ]
    return float(np.mean(scores))

def crossover(parent1: Dict[str, float], parent2: Dict[str, float]) -> Dict[str, float]:
    """BLX-alpha blend crossover."""
    alpha = 0.3
    child = {}
    for k in PARAM_KEYS:
        v1, v2 = parent1[k], parent2[k]
        d = abs(v1 - v2)
        min_v = min(v1, v2) - alpha * d
        max_v = max(v1, v2) + alpha * d
        child[k] = random.uniform(min_v, max_v)
    return clamp_genome(child)

def mutate(genome: Dict[str, float], mutation_rate: float = 0.25) -> Dict[str, float]:
    """Gaussian mutation respecting parameter bounds."""
    mutated = dict(genome)
    for k in PARAM_KEYS:
        if random.random() < mutation_rate:
            low, high = PARAM_SPECS[k]
            scale = (high - low) * 0.15
            mutated[k] += random.gauss(0, scale)
    return clamp_genome(mutated)

def run_genetic_algorithm(
    population_size: int = 28,
    generations: int = 150,
    matches_per_eval: int = 16,
    seed_genome: Dict[str, float] = None,
    workers: int = 12,
    num_players: int = 5,
    export_path: str = None,
) -> Dict[str, float]:
    """
    Run Genetic Algorithm optimization using multi-core evaluation and seeded population.
    """
    if export_path is None:
        export_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ga_weights.pkl')

    if seed_genome is None and os.path.exists(export_path):
        try:
            with open(export_path, 'rb') as f:
                seed_genome = pickle.load(f)
            print(f"Loaded existing champion seed genome from: {export_path}")
        except Exception:
            seed_genome = None

    print(f"\n========================================================")
    print(f"  GENETIC ALGORITHM EVOLUTIONARY TRAINING ({num_players}-PLAYER TABLE)")
    print(f"  Population: {population_size} | Generations: {generations} | Matches/Eval: {matches_per_eval}")
    print(f"  Workers: {workers} cores | Table Size: {num_players} Players | Seeded: {'Yes' if seed_genome else 'Random'}")
    print(f"========================================================\n")

    start_time = time.time()
    # Initialize population (seeded with previous champion and mutations if available)
    population = []
    if seed_genome:
        population.append(copy.deepcopy(seed_genome))
        for _ in range(population_size // 3):
            population.append(mutate(copy.deepcopy(seed_genome), mutation_rate=0.18))
    while len(population) < population_size:
        population.append(random_genome())

    best_overall_genome = copy.deepcopy(seed_genome) if seed_genome else None
    if seed_genome:
        seed_scores = [play_match(seed_genome, num_turns=4, champion_genome=seed_genome, num_players=num_players) for _ in range(matches_per_eval * 2)]
        best_overall_fitness = float(np.mean(seed_scores))
        print(f"Current Champion Baseline Fitness: {best_overall_fitness:+.2f} pts across {matches_per_eval * 2} validation matches ({num_players} players)\n")
    else:
        best_overall_fitness = float('-inf')

    # Worker pool for parallel evaluations
    pool = Pool(processes=workers)

    try:
        for gen in range(generations):
            gen_start = time.time()
            
            # Prepare parallel eval arguments
            eval_champion = best_overall_genome if best_overall_genome else seed_genome
            eval_args = [(ind, matches_per_eval, eval_champion, num_players) for ind in population]
            
            fitness_scores = pool.map(_eval_individual_worker, eval_args)

            gen_best_idx = int(np.argmax(fitness_scores))
            gen_best_fitness = fitness_scores[gen_best_idx]
            gen_avg_fitness = float(np.mean(fitness_scores))

            if gen_best_fitness > best_overall_fitness:
                best_overall_fitness = gen_best_fitness
                best_overall_genome = copy.deepcopy(population[gen_best_idx])
                # Checkpoint save on new record
                with open(export_path, 'wb') as f:
                    pickle.dump(best_overall_genome, f)

            gen_time = time.time() - gen_start
            if (gen + 1) % 10 == 0 or gen == 0 or gen == generations - 1:
                print(f"Gen {gen + 1:03d}/{generations:03d} - Best: {gen_best_fitness:+.2f} pts | Avg: {gen_avg_fitness:+.2f} pts | All-Time: {best_overall_fitness:+.2f} pts ({gen_time:.2f}s)")

            # Selection: Tournament selection (k=3)
            selected_parents = []
            for _ in range(population_size):
                k_indices = random.sample(range(population_size), 3)
                best_k = max(k_indices, key=lambda idx: fitness_scores[idx])
                selected_parents.append(population[best_k])

            # Reproduction: Elitism (keep top 2 + best overall) + Crossover + Mutation
            sorted_indices = np.argsort(fitness_scores)[::-1]
            next_gen = [copy.deepcopy(population[sorted_indices[0]]), copy.deepcopy(population[sorted_indices[1]])]
            if best_overall_genome:
                next_gen.append(copy.deepcopy(best_overall_genome))

            while len(next_gen) < population_size:
                p1, p2 = random.sample(selected_parents, 2)
                child = crossover(p1, p2)
                child = mutate(child)
                next_gen.append(child)

            population = next_gen
    finally:
        pool.close()
        pool.join()

    total_time = time.time() - start_time
    print(f"\nGA Optimization Finished in {total_time:.1f}s! All-Time Best Fitness: {best_overall_fitness:+.2f} pts")
    print(f"Best Evolved Parameters:")
    for k, v in best_overall_genome.items():
        print(f"  {k}: {v:.4f}")

    with open(export_path, 'wb') as f:
        pickle.dump(best_overall_genome, f)
    print(f"Saved latest champion weights to: {export_path}")

    return best_overall_genome

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Run Evolutionary Genetic Algorithm for EstiMania Bots")
    parser.add_argument("--players", type=int, default=5, help="Number of players at the table (default: 5)")
    parser.add_argument("--generations", type=int, default=200, help="Number of generations to evolve (default: 200)")
    parser.add_argument("--pop-size", type=int, default=24, help="Population size (default: 24)")
    parser.add_argument("--matches", type=int, default=14, help="Matches per individual evaluation (default: 14)")
    parser.add_argument("--workers", type=int, default=16, help="Worker processes (default: 16)")
    args = parser.parse_args()

    run_genetic_algorithm(
        population_size=args.pop_size,
        generations=args.generations,
        matches_per_eval=args.matches,
        workers=args.workers,
        num_players=args.players,
    )

