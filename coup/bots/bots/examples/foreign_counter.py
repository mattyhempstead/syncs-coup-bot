from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

import random
import json
from typing import Optional


class ExampleForeignCounter(BaseBot):
    """
        The example Foreign Counter bot.

        https://github.com/syncs-usyd/coup-example-submissions/blob/master/examples/foreign_counter.py
    """

    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.current_player.balance >= 7:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Coup, target_player.player_id)

        return (PrimaryAction.ForeignAid, None)

    def counter_action_handler(self) -> CounterAction:
        action = self.game_info.get_history_primary_action()

        if action.action == PrimaryAction.ForeignAid:
            return CounterAction.BlockForeignAid

        return CounterAction.NoCounterAction

    def challenge_action_handler(self) -> ChallengeAction:
        # No joke this is literally what the example does
        if random.randint(1,10) == 10:
            return ChallengeAction.Challenge

        return ChallengeAction.NoChallenge

