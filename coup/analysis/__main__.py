import numpy as np

from coup.engine.engine import Engine
from coup.bots.bots.base_bot import BaseBot
from coup.bots.bots.other_bot import OtherBot

if __name__ == "__main__":
    BOT_CLASSES = [BaseBot, BaseBot, BaseBot, BaseBot, OtherBot]
    # BOT_CLASSES = [OtherBot, BaseBot, OtherBot, BaseBot, BaseBot]
    GAME_COUNT = 1000

    ties = 0
    winners = []
    for i in range(GAME_COUNT):
        print(f"Game {i}/{GAME_COUNT}", end="\r")

        engine = Engine(BOT_CLASSES, debug=False, shuffle_players=True)
        engine.run_game()

        if engine.tied:
            ties += 1
        else:
            winner = engine.winner
            winners.append(winner.player_id)

    print("")
    print(f"Ties: {ties}")
    print(f"Full games: {GAME_COUNT - ties}")
    print(np.array(np.unique(winners, return_counts=True)).T)
