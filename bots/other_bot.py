from bots.enums import *
from bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

from typing import Optional


class OtherBot(BaseBot):
    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.balances[self.game_info.player_id] >= 7:
            target_player_id = self.get_next_alive_player()
            return (PrimaryAction.Coup, target_player_id)
        elif Character.Duke in self.game_info.own_cards:
            return (PrimaryAction.Tax, None)
        elif Character.Assassin in self.game_info.own_cards and self.game_info.balances[self.game_info.player_id] >= 3:
            target_player_id = self.get_next_alive_player()
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
