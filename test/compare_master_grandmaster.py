import random
import os
import copy
from estimania.player import Player
from estimania.bot_player import BotPlayer
from estimania.game_rules import GameRules
from estimania.game_engine import GameEngine

class SilentEvents:
    def round_announce(self, text): pass
    def score(self, players): pass
    def turn_of(self, player): pass
    def table(self, cards_str, names): pass
    def trick_winner(self, highest_card): pass
    def final_scores(self, players): pass
    def error(self, player, message): pass
    def private_table(self, viewer, cards_str, other_players): pass

def run_head_to_head(matches=200):
    print(f"Running {matches} Head-to-Head Matches: GrandmasterBot vs Pure Heuristic Bot...")
    gm_scores = 0
    h_scores = 0
    gm_wins = 0
    h_wins = 0

    for m in range(matches):
        p_gm = BotPlayer("Grandmaster")
        p_other = BotPlayer("Challenger")
        # Disable sabotage and GA on challenger
        p_other.ga_weights = None
        p_other.play_engine.sabotage_weight = 0.0

        players = [p_gm, p_other]
        random.shuffle(players)

        engine = GameEngine(GameRules(max_turns=4), players, SilentEvents())
        engine.run()

        for p in players:
            if p.username == "Grandmaster":
                gm_scores += p.score
            else:
                h_scores += p.score

        if p_gm.score > p_other.score:
            gm_wins += 1
        elif p_other.score > p_gm.score:
            h_wins += 1

    print(f"GrandmasterBot: Wins {gm_wins} ({gm_wins/matches*100:.1f}%), Avg Score: {gm_scores/matches:.2f}")
    print(f"ChallengerBot : Wins {h_wins} ({h_wins/matches*100:.1f}%), Avg Score: {h_scores/matches:.2f}")

if __name__ == '__main__':
    run_head_to_head(250)
