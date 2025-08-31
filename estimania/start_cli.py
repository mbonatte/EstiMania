from estimania.game_rules import GameRules
from estimania.game_engine import GameEngine
from estimania.game_events_cli import CLIEvents
from estimania.bot_player import BotPlayer

players = [BotPlayer("Alice"), BotPlayer("Bot")]
engine = GameEngine(GameRules(2), players, CLIEvents())
engine.run()
