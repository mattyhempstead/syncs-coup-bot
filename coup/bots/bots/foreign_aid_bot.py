from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

import json
from typing import Optional


class ForeignAidBot(BaseBot):
    """
        An interface on the primary_money_handler that will try to use ForeignAid tactically.
    """
    def primary_money_handler(self) -> tuple[PrimaryAction, Optional[int]]:

        # Get $2 from Foreign Aid if nobody has historically countered it
        if not self.game_info.exists_historical_counter(CounterAction.BlockForeignAid):
            return (PrimaryAction.ForeignAid, None)

        # Otherwise get $1 from Income by default
        return (PrimaryAction.Income, None)
