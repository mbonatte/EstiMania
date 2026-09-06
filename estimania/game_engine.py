# game_engine.py
import time
from typing import List

from estimania.player import Player

from estimania.game_rules import GameRules
from estimania.game_events import GameEvents

class GameEngine:
    def __init__(self, rules: GameRules, players: List[Player], events: GameEvents, bot_delay: float = 0.0, trick_delay: float = 0.0):
        self.rules = rules
        self.players = players
        self.events = events
        self.bot_delay = bot_delay
        self.trick_delay = trick_delay
        self.matches = []
        self.bets = []
        self.cards_in_table = []
        self.current_bettor = -1
        self.current_player_to_drop = 0

    def _collect_bets(self):
        self.current_bettor = (self.current_bettor + 1) % len(self.players)
        order = self.players[self.current_bettor:] + self.players[:self.current_bettor]
        self.bets = [-1] * len(order)
        for i, p in enumerate(order):
            self.events.turn_of(p)
            if self.bot_delay > 0 and hasattr(p, "mlp_model"):
                time.sleep(self.bot_delay)
            p.set_bet(self.bets)
            self.bets[i] = p.bet
            self.events.score(self.players)

        # Notify players of all placed contracts for adversarial sabotage
        contracts = {q.username: q.bet for q in self.players if q.bet is not None}
        for p in self.players:
            if hasattr(p, "on_bets_placed"):
                p.on_bets_placed(contracts)

    def _play_select_card_turn(self, player, current_table, active_names=None):
        """
        Loop until the player provides a valid card (via player.select_card).
        """
        while True:
            if self.bot_delay > 0 and hasattr(player, "mlp_model"):
                time.sleep(self.bot_delay)
            if hasattr(player, "select_card_with_context") and active_names:
                card_played = player.select_card_with_context(current_table, active_names)
            else:
                card_played = player.select_card(current_table)

            if card_played is False:
                # timeout/invalid
                self.events.error(player, "Please select a valid card")
            else:
                return card_played
    
    def _play_one_trick(self):
        self.cards_in_table = []
        order = self.players[self.current_player_to_drop:] + self.players[:self.current_player_to_drop]
        active_names = [q.username for q in order]
        for p in order:
            self.events.turn_of(p)
            card = self._play_select_card_turn(p, self.cards_in_table, active_names=active_names)
            self.cards_in_table.append(card)
            self.events.table([str(c) for c in self.cards_in_table], active_names)

        winner, highest = self.rules.evaluate_trick_winner(self.cards_in_table, self.current_player_to_drop)
        
        self.players[winner].score_in_turn += 1
        winner_username = self.players[winner].username
        for p in self.players:
            if hasattr(p, "on_trick_completed"):
                p.on_trick_completed(self.cards_in_table, winner, highest, winner_name=winner_username)
        self.events.trick_winner(highest)
        self.events.score(self.players)
        
        # Pacing: brief pause so players can clearly see the winning card before the table clears!
        if self.trick_delay > 0:
            time.sleep(self.trick_delay)

        self.current_player_to_drop = winner

    def _init_round(self, n_cards: int):
        match_scores = {q.username: q.score for q in self.players}
        for p in self.players:
            if hasattr(p, "on_match_scores_updated"):
                p.on_match_scores_updated(match_scores)
            if hasattr(p, "on_round_started"):
                p.on_round_started(n_cards)
        self.rules.deal(self.players, n_cards)
        self._collect_bets()
        self.current_player_to_drop = self.current_bettor
        for _ in range(n_cards):
            self._play_one_trick()
        for p in self.players:
            p.check_points()

    def _final_round(self):
        cards = self.rules.draw_random_cards(len(self.players))

        hidden = {p:cards[i] for i, p in enumerate(self.players)}
        # show others' cards privately to each viewer
        for viewer in self.players:
            table = [str(hidden[other]) for other in self.players if other is not viewer]
            other_players = [other for other in self.players if other is not viewer]
            if hasattr(viewer, "see_opponents_cards"):
                viewer.see_opponents_cards(table, other_players)
            if hasattr(self.events, "private_table"):
                self.events.private_table(viewer, table, other_players)

        self._collect_bets()

        winner_idx, _highest = self.rules.evaluate_trick_winner(cards)
        
        self.players[winner_idx].score_in_turn += 1
        for p in self.players:
            p.check_points()

    def run(self):
        self.events.score(self.players)
        self.matches = self.rules.build_match_sequence(len(self.players))

        for i, m in enumerate(self.matches[:-1]):
            self.events.round_announce(f"Round {i+1} | {m} cards")
            self._init_round(m)

        self.events.round_announce("Final Round!")
        self._final_round()

        self.events.final_scores(self.players)

