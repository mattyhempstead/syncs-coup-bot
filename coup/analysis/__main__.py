import pandas as pd
import numpy as np
from random import shuffle
from pathlib import Path

from coup.engine.engine import Engine
from coup.bots.bots.base_bot import BaseBot
from coup.bots.bots.other_bot import OtherBot
from coup.bots.bots.primary_action_bot import PrimaryActionBot
from coup.bots.bots.foreign_aid_bot import ForeignAidBot


def test_bots(bot_classes, game_count):
    """
        Plays games on bots.
    """

    print(f"Playing {game_count} games...")
    for i,b in enumerate(bot_classes):
        print(f"bot{i} = {b}")
    print()

    results = {
        "game_num": [],     # Game number (index from 0)
        "turns": [],        # Number of turns in game
        "tie": [],          # Whether or not game was a tie
        "bot_num": [],      # Index of bot as provided in bot_classes
        "bot_name": [],     # Name of bot class (cls.__name__)
        "table_pos": [],    # Table position of bot in game
        "game_rank": []     # Final rank of bot in game (-1 if tie)
    }

    player_order = list(range(len(bot_classes)))

    for g in range(game_count):
        print(f"Game {g}/{GAME_COUNT}", end="\r")

        shuffle(player_order)

        bot_classes_ordered = [bot_classes[k] for k in player_order]
        engine = Engine(bot_classes_ordered, debug=False)
        engine.run_game()

        # Table positions ordered by final rank
        player_rank = [p.player_id for p in engine.eliminated_players]
        player_rank += [p.player_id for p in engine.remaining_players]
        player_rank.reverse()

        # Bot numbers ordered by final rank
        bot_rank = [player_order[i] for i in player_rank]

        # If more than one player remains then they each tie
        remaining_players_num = len(engine.remaining_players)
        if remaining_players_num == 1:
            tied_players_num = 0
        else:
            tied_players_num = remaining_players_num

        # Add one row for each bot
        for i,b in enumerate(bot_classes):
            results["game_num"].append(g)
            results["turns"].append(engine.turn)
            results["tie"].append(engine.tied)

            results["bot_num"].append(i)
            results["bot_name"].append(b.__name__)

            results["table_pos"].append(player_order.index(i))

            # Bot final game rank (-1 if tie)
            game_rank = bot_rank.index(i)
            if game_rank < tied_players_num:
                game_rank = -1
            results["game_rank"].append(game_rank)


    df = pd.DataFrame(results)
    return df


if __name__ == "__main__":

    BOT_CLASSES = [OtherBot, BaseBot, BaseBot, BaseBot, BaseBot]
    # BOT_CLASSES = [BaseBot, BaseBot, BaseBot, BaseBot, BaseBot]
    # BOT_CLASSES = [OtherBot, ForeignAidBot, PrimaryActionBot, BaseBot, BaseBot]
    # BOT_CLASSES = [OtherBot, ForeignAidBot, PrimaryActionBot, BaseBot, BaseBot]

    GAME_COUNT = 1000

    df = test_bots(BOT_CLASSES, GAME_COUNT)
    # print(df)
    # df.to_csv(str(Path(__file__).parent) + '/results.csv')

    # Dataframe with one row per game 
    df_game_group = df[["game_num", "turns", "tie"]].drop_duplicates().reset_index(drop=True)
    print(df_game_group)
    
    tie_count = df_game_group["tie"].sum()
    print(f"Ties: {tie_count}")
    print(f"Full games: {GAME_COUNT - tie_count}")

    # Prints the number of times each bot won
    print("\nWinning bots cumulative")
    df_winner = df[df["game_rank"] == 0]
    # print(df_winner.groupby(["bot_num", "bot_name"]).())
    print(df_winner.value_counts(["bot_num", "bot_name"]))

    # Bot num VS game rank
    print("\nbot_num VS game_rank")
    bot_results = pd.crosstab(df["bot_num"], df["game_rank"])
    print(bot_results)
    print(bot_results / GAME_COUNT)

    # Bot0 table position VS game rank
    print("\nbot0 table_pos VS game_rank")
    print(BOT_CLASSES[0])
    df_bot0 = df[df["bot_num"] == 0]
    bot0_results = pd.crosstab(df_bot0["game_rank"], df_bot0["table_pos"])
    print(bot0_results)

