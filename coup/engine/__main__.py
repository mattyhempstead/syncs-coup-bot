from coup.engine.engine import Engine
from coup.bots.base_bot import BaseBot

if __name__ == "__main__":
    engine = Engine([BaseBot] * 5)
    engine.run_game()