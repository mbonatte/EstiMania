from flask_socketio import emit

def _emit_score(players, room_id):
    score = [
        {'name': p.username, 'bet': p.bet, 'wins': p.score_in_turn}
        for p in players if getattr(p, 'room_id', room_id) == room_id
    ]
    emit('score', score, to=room_id)

def _emit_final_score(players, room_id):
    scores = [{'name': p.username, 'score': p.score}
              for p in players if getattr(p, 'room_id', room_id) == room_id]
    scores = sorted(scores, key=lambda d: d['score'], reverse=True)
    emit('final-score', scores, to=room_id)

class GameOnline:
    """
    Online/session layer: handles turn order, prompting players, emitting updates.
    Delegates pure decisions to GameRules.
    """

    def __init__(self, room_id, players, rules):
        self.room_id = room_id
        self.players = players
        self.rules = rules

        self.matches = []
        self.cards_in_table = []
        self.current_player_to_bet = -1
        self.current_player_to_drop = 0  # leader for current trick

        _emit_score(self.players, self.room_id)

    # ---------- small emit helpers ----------

    def _emit_turn_of(self, player):
        emit('turn', player.username, to=self.room_id)

    def _emit_table(self, players_view):
        table = [str(card) for card in self.cards_in_table]
        names = [p.username for p in players_view]
        emit('table', {'table': table, 'names': names}, to=self.room_id)

    def _emit_winner_card(self, card):
        emit('winner-card', str(card), to=self.room_id)

    # ---------- player I/O helpers ----------

    def _play_select_card_turn(self, player, current_table):
        """
        Loop until the player provides a valid card (via player.select_card).
        """
        while True:
            card_played = player.select_card(current_table)
            if card_played is False:
                # timeout/invalid
                emit('error', "Please select a valid card", to=getattr(player, 'connection_id', self.room_id))
            else:
                return card_played
    
    # ---------- betting & turn orchestration ----------

    def set_bets(self):
        """
        Ask players for bets in the correct order, update scores display as we go.
        (No rules logic here beyond ordering; collecting bets is "I/O".)
        """
        self.current_player_to_bet = (self.current_player_to_bet + 1) % len(self.players)

        order = self.players[self.current_player_to_bet:] + self.players[:self.current_player_to_bet]
        bets = [-1] * len(order)

        for i, player in enumerate(order):
            self._emit_turn_of(player)
            player.set_bet(bets)
            bets[i] = player.bet
            _emit_score(self.players, self.room_id)

    def _play_trick(self, n_players):
        """
        Play a single trick of the given round:
        - Determine play order starting from current leader
        - Gather one card per player
        - Ask GameRules who won, update leader for next trick
        """
        self.cards_in_table = []

        order = self.players[self.current_player_to_drop:] + self.players[:self.current_player_to_drop]

        for p in order:
            self._emit_turn_of(p)
            played = self._play_select_card_turn(p, self.cards_in_table)
            self.cards_in_table.append(played)
            self._emit_table(order)

        # Winner
        winner, highest = self.rules.evaluate_trick_winner(
            cards_in_table=self.cards_in_table,
            starting_index_player=self.current_player_to_drop
        )

        # Map rotated offset back to absolute index
        self.players[winner].score_in_turn += 1

        self._emit_winner_card(highest)
        _emit_score(self.players, self.room_id)

        # Next trick leader is the winner
        self.current_player_to_drop = winner

    def play_round(self, n_cards):
        """
        One round of n_cards:
        - leader for first trick is whoever just finished betting (as in your original logic)
        - play n_cards tricks
        """
        # First trick leader = player who started betting sequence
        self.current_player_to_drop = self.current_player_to_bet

        for _ in range(n_cards):
            self._play_trick(len(self.players))

    # ---------- end-to-end round flows ----------

    def initiate_round(self, n_cards):
        self.rules.deal(self.players, n_cards)
        self.set_bets()
        self.play_round(n_cards)
        for p in self.players:
            p.check_points()

    def final_round(self):
        """
        Final round:
        - Each player draws 1 hidden card.
        - Show *other players'* cards to each player.
        - Take bets.
        - Reveal/evaluate winner.
        - Update points.
        """
        self.rules.deal(self.players, 1)
        faceup_cards = [p.hand[0] for p in self.players]

        # Show others' cards to each player
        for p in self.players:
            table = [str(other.hand[0]) for other in self.players if other is not p]
            names = [other.username for other in self.players if other is not p]
            if hasattr(p, 'connection_id'):
                # This is a NetworkPlayer
                emit('table', {'table': table, 'names': names}, to=p.connection_id)

        self.set_bets()

        winner_idx, _highest = self.rules.evaluate_trick_winner(faceup_cards)
        self.players[winner_idx].score_in_turn += 1

        for p in self.players:
            p.check_points()
    
    # ---------- game loop ----------

    def run(self):
        _emit_score(self.players, self.room_id)

        self.matches = self.rules.build_match_sequence(len(self.players))

        # All but the last are normal rounds
        for i, m in enumerate(self.matches[:-1]):
            emit('round', f'Round {i+1} | {m} cards', to=self.room_id)
            self.initiate_round(m)

        # Final
        emit('round', 'Final Round!', to=self.room_id)
        self.final_round()

        _emit_final_score(self.players, self.room_id)