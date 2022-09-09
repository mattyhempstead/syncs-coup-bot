from bots.enums import *

"""END LOCAL IMPORTS"""

from typing import Optional


class Action:
    def __init__(self, dict: dict[str, str]) -> None:
        # The ActionType of the action.
        self.action_type: ActionType = ActionType(int(dict['action_type']))

        # The Action of the action.
        if self.action_type == ActionType.PrimaryAction:
            self.action: ActionEnum = PrimaryAction(int(dict['action']))
        elif self.action_type == ActionType.CounterAction:
            self.action = CounterAction(int(dict['action']))
        else:
            self.action = ChallengeAction(int(dict['action']))

        # The player that made the action.
        self.player: int = int(dict['player'])

        # The targeted player of the action if it exists.
        self.target: Optional[int] = None
        if dict['target'] is not None:
            self.target = int(dict['target'])

        # Says whether the move successfully happened or was challenged and
        # failed.
        self.successful: bool = bool(dict['successful'])
        