from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

import random
import json
from typing import Optional


class ExampleCounter(BaseBot):
    """
        The example Counter bot.

        https://github.com/syncs-usyd/coup-example-submissions/blob/master/examples/counter.py
    """

    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.current_player.balance >= 7:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Coup, target_player.player_id)

        return (PrimaryAction.Income, None)

    def counter_action_handler(self) -> CounterAction:
        action = self.game_info.get_history_primary_action()

        if action.action == PrimaryAction.Assassinate:
            return CounterAction.BlockAssassination

        if action.action == PrimaryAction.ForeignAid:
            return CounterAction.BlockForeignAid

        if action.action == PrimaryAction.Steal:
            # NOTE: technically the example bot maintains a state and will alternatie
            # We just select randomly bc its easier
            if random.random() < 0.5:
                return CounterAction.BlockStealingAsCaptain
            else:
                return CounterAction.BlockStealingAsAmbassador

        return CounterAction.NoCounterAction
