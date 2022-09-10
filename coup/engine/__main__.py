from coup.engine.engine import Engine
from coup.bots.base_bot import BaseBot
from coup.bots.other_bot import OtherBot

if __name__ == "__main__":
    engine = Engine([BaseBot, BaseBot, BaseBot, BaseBot, OtherBot])
    engine.run_game()
