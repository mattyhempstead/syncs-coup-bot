from coup.bots.enums import *

"""END LOCAL IMPORTS"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Action:
    action_type: ActionType
    action: ActionEnum
    player: int
    target: Optional[int]
    successful: bool

    @staticmethod
    def from_dictionary(dict: dict[str, str]) -> 'Action':
        # The ActionType of the action.
        action_type: ActionType = ActionType(int(dict['action_type']))

        # The Action of the action.
        if action_type == ActionType.PrimaryAction:
            action: ActionEnum = PrimaryAction(int(dict['action']))
        elif action_type == ActionType.CounterAction:
            action = CounterAction(int(dict['action']))
        else:
            action = ChallengeAction(int(dict['action']))

        # The player that made the action.
        player: int = int(dict['player'])

        # The targeted player of the action if it exists.
        target: Optional[int] = None
        if dict['target'] is not None:
            target = int(dict['target'])

        # Says whether the move successfully happened or was challenged and
        # failed.
        successful: bool = bool(dict['successful'])

        return Action(
            action_type=action_type,
            action=action,
            player=player,
            target=target,
            successful=successful
        )