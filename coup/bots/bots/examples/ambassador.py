from coup.common.rules import *
from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

import json
from typing import Optional


class ExampleAmbassador(BaseBot):
    """
        The example Ambassador bot.

        https://github.com/syncs-usyd/coup-example-submissions/blob/master/examples/ambassador.py
    """

    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.current_player.balance >= 7:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Coup, target_player.player_id)

        elif Character.Ambassador in self.game_info.own_cards:
            return (PrimaryAction.Exchange, None)

        return (PrimaryAction.ForeignAid, None)


    def challenge_action_handler(self) -> ChallengeAction:
        # Seems to do nothing in the example?
        return ChallengeAction.NoChallenge


    def challenge_response_handler(self) -> int:
        """
            Which card number we reveal if we are challenged (for a primary or a counter).

            If we are honest, we usually want to reveal the correct card unless we are mega-braining.
        """
        if ActionType.CounterAction in self.game_info.history[-1]:
            action = self.game_info.get_history_counter_action()

            # Return the right card
            action_card = COUNTER_ACTION_TO_CARD[action.action]
            if action_card in self.game_info.own_cards:
                return self.game_info.get_character_location(action_card)

        else:
            action = self.game_info.get_history_primary_action()

            # Return the right card
            action_card = PRIMARY_ACTION_TO_CARD[action.action]
            if action_card in self.game_info.own_cards:
                return self.game_info.get_character_location(action_card)

        # Reveal first card if we lied
        return 0


    def discard_choice_handler(self) -> int:
        return 0
