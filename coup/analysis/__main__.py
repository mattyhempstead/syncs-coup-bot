import pandas as pd
import numpy as np
import random
from pathlib import Path
from typing import List

from coup.engine.engine import Engine
from coup.bots.bots.base_bot import BaseBot
from coup.bots.bots.other_bot import OtherBot
from coup.bots.bots.other_bot_2 import OtherBot2
from coup.bots.bots.primary_action_bot import PrimaryActionBot
from coup.bots.bots.foreign_aid_bot import ForeignAidBot

from coup.bots.bots.examples.ambassador import ExampleAmbassador
from coup.bots.bots.examples.assassin import ExampleAssassin
from coup.bots.bots.examples.challenger import ExampleChallenger
from coup.bots.bots.examples.counter import ExampleCounter
from coup.bots.bots.examples.foreign_counter import ExampleForeignCounter
from coup.bots.bots.examples.simple import ExampleSimple
from coup.bots.bots.examples.submission_template import ExampleSubmissionTemplate



def select_bots(bot_main:BaseBot, bot_pool:list[BaseBot]) -> List[BaseBot]:
    """ Selects main bot and 4 random choice bots from a pool """
    bot_classes = [bot_main]
    bot_classes += random.sample(bot_pool, 4)
    return bot_classes


def test_bots(game_count:int, bot_main:BaseBot, bot_pool:list[BaseBot]) -> pd.DataFrame:
    """
        Plays games on bots and returns a DataFrame of game results for analysis.
    """



    print(f"Playing {game_count} games...")
    # for i,b in enumerate(bot_classes):
    #     print(f"bot{i} = {b}")
    print()

    results = {
        "game_num": [],     # Game number (index from 0)
        "turns": [],        # Number of turns in game
        "tie": [],          # Whether or not game was a tie
        "bot_name": [],     # Name of bot class (cls.__name__)
        "table_pos": [],    # Table position of bot in game
        "game_rank": []     # Final rank of bot in game (-1 if tie)
    }

    player_order = list(range(5))

    for g in range(game_count):
        print(f"Game {g}/{GAME_COUNT}", end="\r")

        bot_classes = select_bots(bot_main, bot_pool)
        random.shuffle(player_order)

        bot_classes_ordered = [bot_classes[k] for k in player_order]
        # input()
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

    GAME_COUNT = 1000
    
    # The bot we are testing
    # This will be included in all games as bot_num 0
    BOT_MAIN = OtherBot2

    # A collection of bots that are selected from.
    # This should NOT include the bot we are testing if we always want it selected.
    BOT_POOL = [
        # All 7 example bots
        ExampleAmbassador,
        ExampleAssassin,
        ExampleChallenger,
        ExampleCounter,
        ExampleForeignCounter,
        ExampleSimple,
        ExampleSubmissionTemplate,

        # Current leaderboard has 14 other players (not including us)
        OtherBot.as_name("OtherBot_0"),
        OtherBot.as_name("OtherBot_1"),
        OtherBot.as_name("OtherBot_2"),
        OtherBot.as_name("OtherBot_3"),
        OtherBot.as_name("OtherBot_4"),
        OtherBot.as_name("OtherBot_5"),
        OtherBot.as_name("OtherBot_6"),
        OtherBot.as_name("OtherBot_7"),
        OtherBot.as_name("OtherBot_8"),
        OtherBot.as_name("OtherBot_9"),
        OtherBot.as_name("OtherBot_10"),
        OtherBot.as_name("OtherBot_11"),
        OtherBot.as_name("OtherBot_12"),
        OtherBot.as_name("OtherBot_13"),
    ]



    df = test_bots(GAME_COUNT, BOT_MAIN, BOT_POOL)
    # print(df)
    # df.to_csv(str(Path(__file__).parent) + '/results.csv')

    # Dataframe with one row per game 
    df_game = df[["game_num", "turns", "tie"]].drop_duplicates().reset_index(drop=True)
    print(df_game)
    
    tie_count = df_game["tie"].sum()
    print(f"Regular games: {GAME_COUNT - tie_count}")
    print(f"Ties: {tie_count}")

    df_game_regular = df_game[~df_game['tie']]  # Games without ties
    print(f"Average game length (without ties): {df_game_regular['turns'].mean():.2f} turns")

    # Prints the number of times each bot won
    print("\nWinning bots cumulative")
    df_winner = df[df["game_rank"] == 0]
    # print(df_winner.groupby(["bot_num", "bot_name"]).())
    print(df_winner.value_counts(["bot_name"]))

    # NOTE: Only regular game win percentage
    print()
    print(df_winner.value_counts(["bot_name"]) / (GAME_COUNT - tie_count))

    # Bot num VS game rank
    print("\nbot_num VS game_rank")
    bot_results = pd.crosstab(df["bot_name"], df["game_rank"])
    print(bot_results)
    print(bot_results / GAME_COUNT)

    # Bot0 table position VS game rank
    print(f"\n{BOT_MAIN.__name__} table_pos VS game_rank")
    df_bot0 = df[df["bot_name"] == BOT_MAIN.__name__]
    bot0_results = pd.crosstab(df_bot0["game_rank"], df_bot0["table_pos"])
    print(bot0_results)
