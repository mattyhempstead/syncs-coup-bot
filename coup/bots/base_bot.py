from coup.bots.bot_battle import BotBattle
from coup.bots.game_info import GameInfo
from coup.bots.enums import *

"""END LOCAL IMPORTS"""

import json
from typing import Optional


class BaseBot:
    def __init__(self, local_mode=False) -> None:
        game_info: Optional[GameInfo] = None

        self.bot_battle: Optional[BotBattle]
        if not local_mode:
            self.bot_battle = BotBattle()

    def __str__(self) -> str:
        return self.__class__.__name__


    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.current_player.balance >= 7:
            target_player_id = self.game_info.get_next_alive_player()
            return (PrimaryAction.Coup, target_player_id)
        elif Character.Duke in self.game_info.own_cards:
            return (PrimaryAction.Tax, None)
        elif Character.Assassin in self.game_info.own_cards and self.game_info.current_player.balance >= 3:
            target_player_id = self.game_info.get_next_alive_player()
            return (PrimaryAction.Assassinate, target_player_id)
        else:
            return (PrimaryAction.Income, None)

    def counter_action_handler(self) -> CounterAction:
        return CounterAction.NoCounterAction

    def challenge_action_handler(self) -> ChallengeAction:
        return ChallengeAction.NoChallenge

    def challenge_response_handler(self) -> int:
        return 0

    def discard_choice_handler(self) -> int:
        return 0

    def run(self) -> None:
        print("Bot:", str(self), flush=True)

        while True:
            self.game_info = self.bot_battle.get_game_info()
            requested_move = self.game_info.requested_move

            if requested_move == RequestedMove.PrimaryAction:
                primary_action, target = self.primary_action_handler()
                self.bot_battle.play_primary_action(primary_action, target)

            elif requested_move == RequestedMove.CounterAction:
                counter_action = self.counter_action_handler()
                self.bot_battle.play_counter_action(counter_action)

            elif requested_move == RequestedMove.ChallengeAction:
                challenge_action = self.challenge_action_handler()
                self.bot_battle.play_challenge_action(challenge_action)

            elif requested_move == RequestedMove.ChallengeResponse:
                challenge_response = self.challenge_response_handler()
                self.bot_battle.play_challenge_response(challenge_response)

            elif requested_move == RequestedMove.DiscardChoice:
                discard_choice = self.discard_choice_handler()
                self.bot_battle.play_discard_choice(discard_choice)

            else:
                raise Exception(f'Unknown requested move: {requested_move}')

