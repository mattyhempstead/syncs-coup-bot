from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

import random
import json
from typing import Optional


class ExampleSubmissionTemplate(BaseBot):
    """
        The example Submission Template.

        https://github.com/syncs-usyd/coup-example-submissions/blob/master/submission_template.py
    """

    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:
        if self.game_info.current_player.balance >= 7:
            target_player = self.game_info.get_next_alive_player()
            return (PrimaryAction.Coup, target_player.player_id)

        return (PrimaryAction.Income, None)

