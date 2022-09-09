from coup.bots.enums import *
from coup.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

from typing import Optional


class OtherBot(BaseBot):
    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.current_player.balance >= 7:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Coup, target_player.player_id)
        elif Character.Duke in self.game_info.own_cards:
            return (PrimaryAction.Tax, None)
        elif Character.Assassin in self.game_info.own_cards and self.game_info.current_player.balance >= 3:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Assassinate, target_player.player_id)
        elif Character.Captain in self.game_info.own_cards and self.game_info.get_richest_player().balance > 0:
            target_player = self.game_info.get_richest_player()
            print("Stealing from", target_player.player_id, flush=True)
            return (PrimaryAction.Steal, target_player.player_id)
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
