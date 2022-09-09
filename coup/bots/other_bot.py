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
            target_player = self.game_info.get_winning_player()
            return (PrimaryAction.Assassinate, target_player.player_id)
        elif Character.Captain in self.game_info.own_cards and self.game_info.get_richest_player().balance > 0:
            target_player = self.game_info.get_richest_player()
            print("Stealing from", target_player.player_id, flush=True)
            return (PrimaryAction.Steal, target_player.player_id)
        else:
            return (PrimaryAction.Income, None)

    def counter_action_handler(self) -> CounterAction:
        action = self.game_info.get_history_primary_action()

        # Block foreign aid if we can
        if Character.Duke in self.game_info.own_cards:
            if action.action == PrimaryAction.ForeignAid:
                return CounterAction.BlockForeignAid

        # Block assassination if we can
        if Character.Contessa in self.game_info.own_cards:
            if action.action == PrimaryAction.Assassinate:
                return CounterAction.BlockAssassination

        # Block stealing if we can (as Captain)
        if Character.Captain in self.game_info.own_cards:
            if action.action == PrimaryAction.Steal:
                return CounterAction.BlockStealingAsCaptain

        # Block stealing if we can (as Ambassador)
        if Character.Ambassador in self.game_info.own_cards:
            if action.action == PrimaryAction.Steal:
                return CounterAction.BlockStealingAsAmbassador

        return CounterAction.NoCounterAction

    def challenge_action_handler(self) -> ChallengeAction:
        return ChallengeAction.NoChallenge

    def challenge_response_handler(self) -> int:
        """ Which card number we reveal if we are challenged (for a primary or a counter) """
        return 0

    def discard_choice_handler(self) -> int:
        return 0
