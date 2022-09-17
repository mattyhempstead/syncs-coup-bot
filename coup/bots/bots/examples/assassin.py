from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

import json
from typing import Optional


class ExampleAssassin(BaseBot):
    """
        The example Assassin bot.

        https://github.com/syncs-usyd/coup-example-submissions/blob/master/examples/assassin.py
    """

    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.current_player.balance >= 7:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Coup, target_player.player_id)

        if self.game_info.current_player.balance > 3:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Assassinate, target_player.player_id)

        return (PrimaryAction.Income, None)

    def counter_action_handler(self) -> CounterAction:
        action = self.game_info.get_history_primary_action()

        if action.action == PrimaryAction.ForeignAid:
            return CounterAction.BlockForeignAid

        return CounterAction.NoCounterAction

    def discard_choice_handler(self) -> int:
        return 0
