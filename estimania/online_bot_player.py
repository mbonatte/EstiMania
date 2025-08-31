from .bot_player import BotPlayer

class OnlineBotPlayer(BotPlayer):
    def __init__(self, room_id=None, username=None):
        super().__init__(username)
        self.room_id = room_id
