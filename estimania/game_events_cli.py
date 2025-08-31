from estimania.game_events import GameEvents

class CLIEvents(GameEvents):
    def round_announce(self, text): print(text)
    def score(self, players):
        row = " | ".join(f"{p.username}: bet={p.bet}, wins={p.score_in_turn}" for p in players)
        print(f"SCORE: {row}")
    def turn_of(self, player): print(f"TURN: {player.username}")
    def table(self, cards_str, names): print(f"TABLE: {list(zip(names, cards_str))}")
    def trick_winner(self, highest_card): print(f"TRICK WINNER CARD: {highest_card}")
    def final_scores(self, players):
        scores = sorted([(p.username, p.score) for p in players], key=lambda x: x[1], reverse=True)
        print("FINAL:", scores)
    def error(self, player, message): print(f"[{player.username}] ERROR: {message}")
    def private_table(self, viewer, cards_str, other_players):
        names = [p.username for p in other_players]
        print(f"(Private to {viewer.username}) TABLE: {list(zip(names, cards_str))}")
