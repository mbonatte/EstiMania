import random
import os
import pickle
from typing import List
from estimania.player import Player
from estimania.card import Card
from estimania.bot_player import BotPlayer
from estimania.game_rules import GameRules
from estimania.game_engine import GameEngine
from estimania.game_events import GameEvents

class SilentEvents(GameEvents):
    def round_announce(self, text): pass
    def score(self, players): pass
    def turn_of(self, player): pass
    def table(self, cards_str, names): pass
    def trick_winner(self, highest_card): pass
    def final_scores(self, players): pass
    def error(self, player, message): pass
    def private_table(self, viewer, cards_str, other_players): pass

class RandomPlayer(Player):
    """Baseline 0: Random bets and random card selection."""
    def __init__(self, name="Random"):
        super().__init__(name)

    def set_bet(self, current_bets):
        self.bet = random.randint(0, len(self.hand)) if self.hand else random.randint(0, 1)
        return self.bet

    def select_card(self, cards_in_table):
        valid = [c for c in self.hand if self.is_moviment_valid(c, cards_in_table)]
        card = random.choice(valid)
        self.hand.remove(card)
        return card

class LegacyBotPlayer(Player):
    """Baseline 1: Old Bot behavior - 5-feature MLP betting + random card selection."""
    def __init__(self, name="LegacyBot"):
        super().__init__(name)
        legacy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'estimania', 'mlp_model.pkl')
        with open(legacy_path, 'rb') as f:
            data = pickle.load(f)
        self.coefs = data['coefs']
        self.intercepts = data['intercepts']
        self.features = data['features']

    def set_bet(self, current_bets):
        if not self.hand:
            self.bet = 0
            return self.bet
        if len(self.hand) > 5:
            self.bet = random.randint(0, len(self.hand))
            return self.bet

        best_b = 0
        best_r = float('-inf')
        for b in range(len(self.hand) + 1):
            env = {f: -1.0 for f in self.features}
            env['n_adversaries'] = len(current_bets) - 1
            for i, bet_val in enumerate(current_bets[:-1]):
                if f'bet_{i+1}' in env:
                    env[f'bet_{i+1}'] = float(bet_val)
            for i, c in enumerate(self.hand):
                if f'hand_{i+1}' in env:
                    env[f'hand_{i+1}'] = float(int(c))
            env['my_bet'] = float(b)

            vec = [env[k] for k in self.features]
            layer = vec
            for i in range(len(self.coefs) - 1):
                import numpy as np
                layer = np.maximum(0, np.dot(layer, self.coefs[i]) + self.intercepts[i])
            pred = float((np.dot(layer, self.coefs[-1]) + self.intercepts[-1]).flatten()[0])
            if pred > best_r:
                best_r = pred
                best_b = b
        self.bet = best_b
        return self.bet

    def select_card(self, cards_in_table):
        valid = [c for c in self.hand if self.is_moviment_valid(c, cards_in_table)]
        card = random.choice(valid)
        self.hand.remove(card)
        return card

def run_tournament(num_matches=250, num_turns=4):
    print(f"\n========================================================")
    print(f"  RUNNING TOURNAMENT BENCHMARK ({num_matches} Matches, 4 Players)")
    print(f"  Players: [GrandmasterBot, LegacyBot, Random 1, Random 2]")
    print(f"========================================================\n")

    wins = {"Grandmaster": 0, "LegacyBot": 0, "Random1": 0, "Random2": 0}
    total_scores = {"Grandmaster": 0, "LegacyBot": 0, "Random1": 0, "Random2": 0}

    for m in range(num_matches):
        p_master = BotPlayer("Grandmaster")
        p_legacy = LegacyBotPlayer("LegacyBot")
        p_rand1 = RandomPlayer("Random1")
        p_rand2 = RandomPlayer("Random2")

        players = [p_master, p_legacy, p_rand1, p_rand2]
        random.shuffle(players)  # randomize seating position

        engine = GameEngine(GameRules(max_turns=num_turns), players, SilentEvents())
        engine.run()

        # Record scores
        for p in players:
            total_scores[p.username] += p.score

        # Determine winner
        best_score = max(p.score for p in players)
        for p in players:
            if p.score == best_score:
                wins[p.username] += 1

    print("--- 4-PLAYER TOURNAMENT RESULTS ---")
    for name in ["Grandmaster", "LegacyBot", "Random1", "Random2"]:
        avg_score = total_scores[name] / num_matches
        win_pct = (wins[name] / num_matches) * 100
        print(f"{name:15s} | Wins: {wins[name]:3d} ({win_pct:5.1f}%) | Avg Score: {avg_score:6.2f} pts | Total Score: {total_scores[name]:5d}")

    # Head-to-head 2-player match: Grandmaster vs LegacyBot
    print(f"\n========================================================")
    print(f"  HEAD-TO-HEAD MATCH: Grandmaster vs LegacyBot (200 Matches)")
    print(f"========================================================\n")

    h2h_wins = {"Grandmaster": 0, "LegacyBot": 0}
    h2h_scores = {"Grandmaster": 0, "LegacyBot": 0}

    for m in range(200):
        p_master = BotPlayer("Grandmaster")
        p_legacy = LegacyBotPlayer("LegacyBot")
        players = [p_master, p_legacy]
        random.shuffle(players)

        engine = GameEngine(GameRules(max_turns=num_turns), players, SilentEvents())
        engine.run()

        for p in players:
            h2h_scores[p.username] += p.score

        best = max(p.score for p in players)
        for p in players:
            if p.score == best:
                h2h_wins[p.username] += 1

    for name in ["Grandmaster", "LegacyBot"]:
        avg_score = h2h_scores[name] / 200
        win_pct = (h2h_wins[name] / 200) * 100
        print(f"{name:15s} | Wins: {h2h_wins[name]:3d} ({win_pct:5.1f}%) | Avg Score: {avg_score:6.2f} pts")

if __name__ == '__main__':
    run_tournament()
