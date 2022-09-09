from coup.bots.enums import *
from coup.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

from typing import Optional


class OtherBot(BaseBot):
    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:

        # We must coup if we can afford it
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
            print("Stealing from", target_player.player_id, flush=True)
            return (PrimaryAction.Steal, target_player.player_id)

        else:
            # Get $2 from Foreign Aid if nobody has historically countered it
            if not self.game_info.exists_historical_counter(CounterAction.BlockForeignAid):
                return (PrimaryAction.ForeignAid, None)

            # Otherwise get $1 from Income by default
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
        """
        TODO: Conservative check we should challenge if not challenging results in certain loss
        TODO: Conservative check we should challenge when logically impossible (e.g. revealed cards + our cards == 3 of char)

        TODO: Likely scenarios of faking
          - A player avoids countering when possible (e.g. on a foreign aid), then claims the benefit from that card (e.g. tax)
          - A player calls Contessa when they have one card left (since they will lose unless they counter)
        """

        return ChallengeAction.NoChallenge

    def challenge_response_handler(self) -> int:
        """
            Which card number we reveal if we are challenged (for a primary or a counter).

            If we are honest, we usually want to reveal the correct card unless we are mega-braining.
        """
        if ActionType.CounterAction in self.game_info.history[-1]:
            action = self.game_info.get_history_counter_action()

            # Reveal Duke if we are challenged for Blocking ForeignAid
            if action.action == CounterAction.BlockForeignAid and Character.Duke in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Duke)

        else:
            action = self.game_info.get_history_primary_action()

            # Reveal Captain if we are challenged for Stealing
            if action.action == PrimaryAction.Steal and Character.Captain in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Captain)

            # Reveal Assassin if we are challenged for Assassinating
            if action.action == PrimaryAction.Assassinate and Character.Assassin in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Assassin)

        return 0

    def discard_choice_handler(self) -> int:
        return 0
