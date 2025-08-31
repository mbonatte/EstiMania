import unittest
import random
from typing import List, Dict, Any

from estimania.player import Player
from estimania.game_rules import GameRules
from estimania.game_events import GameEvents
from estimania.game_engine import GameEngine

class FakePlayer(Player):
    def __init__(self, name):
        super().__init__(name)
    
    def select_card(self, cards_on_table):
        return self.hand.pop(0)
    
    def set_bet(self, bets_so_far):
        self.bet = 0
        return self.bet
class FakeEvents:
    """
    Captures GameEngine event calls for assertions.
    """
    def __init__(self):
        self.round_announcements: List[str] = []
        self.scores_payloads: List[List[FakePlayer]] = []
        self.turns: List[str] = []
        self.tables: List[dict] = []
        self.trick_winners: List[Any] = []
        self.final_scores_payloads: List[List[FakePlayer]] = []
        self.errors: List[tuple] = []
        self.private_tables: List[tuple] = []

    def round_announce(self, text: str) -> None:
        self.round_announcements.append(text)

    def score(self, players: List[FakePlayer]) -> None:
        # store by reference (ok for our assertions)
        self.scores_payloads.append(list(players))

    def turn_of(self, player: FakePlayer) -> None:
        self.turns.append(player.username)

    def table(self, cards_str: List[str], names: List[str]) -> None:
        self.tables.append({"cards": list(cards_str), "names": list(names)})

    def trick_winner(self, highest_card) -> None:
        self.trick_winners.append(highest_card)

    def final_scores(self, players: List[FakePlayer]) -> None:
        self.final_scores_payloads.append(list(players))

    def error(self, player: FakePlayer, message: str) -> None:
        self.errors.append((player.username, message))

    def private_table(self, viewer: FakePlayer, cards_str: List[str], names: List[str]) -> None:
        self.private_tables.append((viewer.username, list(cards_str), list(names)))

class GameEngineTests(unittest.TestCase):
    def setUp(self):
        self.rules = GameRules(2)
        self.events = FakeEvents()
        self.p1 = FakePlayer("Alice")
        self.p2 = FakePlayer("Bob")
        self.engine = GameEngine(rules=self.rules, players=[self.p1, self.p2], events=self.events)

    def test_run_triggers_round_and_final(self):
        self.engine.run()

        # Round announcements include one normal round and the final round
        self.assertIn("Round 2 | 2 cards", self.events.round_announcements[1])
        self.assertIn("Final Round!", self.events.round_announcements[-1])

        # At least one score emit at start and several during play
        self.assertGreaterEqual(len(self.events.scores_payloads), 1)

        # Final scores emitted once at the end
        self.assertEqual(len(self.events.final_scores_payloads), 1)

    def test_trick_flow_and_scoring(self):
        random.seed(0)
        self.engine.run()

        # In the normal round (2 cards each), two tricks occur.
        self.assertEqual(len(self.events.trick_winners), 5)
        self.assertIn('13 of Hearts', str(self.events.trick_winners[0]))
        self.assertIn('13 of Clubs', str(self.events.trick_winners[-1]))

        # After the normal round, check_points moves score_in_turn into score and resets score_in_turn.
        final_players = self.events.final_scores_payloads[0]
        # Build a mapping of username -> score
        final_scores = {p.username: p.score for p in final_players}
        self.assertEqual(final_scores["Alice"], -2)
        self.assertEqual(final_scores["Bob"], 0)

    def test_private_table_called_for_final_round(self):
        random.seed(0)
        self.engine.run()

        # private_table should be sent once per viewer in final round
        viewers = [entry[0] for entry in self.events.private_tables]
        self.assertCountEqual(viewers, ["Alice", "Bob"])

        # Each viewer does NOT see their own card in the private view; only opponents' cards (strings)
        for viewer, cards_str, player in self.events.private_tables:
            print()
            if viewer == "Alice":
                # Alice sees only Bob's card/name
                self.assertEqual(player[0].username, "Bob")
                self.assertEqual(cards_str, ["12 of Diamonds"])
            elif viewer == "Bob":
                self.assertEqual(player[0].username, "Alice")
                self.assertEqual(cards_str, ["10 of Hearts"])

if __name__ == "__main__":
    unittest.main()