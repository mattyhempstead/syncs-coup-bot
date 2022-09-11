from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

import json
from typing import Optional


class PrimaryActionBot(BaseBot):
    """
        A bot interface that will perform primary Character actions in some given order of priority.
        If not possible, it will play Income.
    """

    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        # We must coup if we can afford it (technically if >=10)
        if self.game_info.current_player.balance >= 7:
            target_player = self.game_info.get_winning_player()
            return (PrimaryAction.Coup, target_player.player_id)

        elif Character.Duke in self.game_info.own_cards:
            return (PrimaryAction.Tax, None)

        elif Character.Assassin in self.game_info.own_cards and self.game_info.current_player.balance >= 3:
            target_player = self.game_info.get_winning_player()
            return (PrimaryAction.Assassinate, target_player.player_id)

        elif Character.Captain in self.game_info.own_cards and self.game_info.get_richest_player().balance > 0:
            target_player = self.game_info.get_richest_player()
            #print("Stealing from", target_player.player_id, flush=True)
            return (PrimaryAction.Steal, target_player.player_id)

        else:
            return self.primary_money_handler()
