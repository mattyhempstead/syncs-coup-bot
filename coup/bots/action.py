from coup.bots.enums import *
from coup.common.rules import *

"""END LOCAL IMPORTS"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Action:
    action_type: ActionType
    action: ActionEnum
    player_id: int
    successful: Optional[bool]
    target: Optional[int] = None

    @staticmethod
    def from_dictionary(dict) -> 'Action':
        # TODO: Make type safe.
        # TODO: Work out if the type casts can be removed?
        
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
        player_id: int = int(dict['player'])

        # The targeted player of the action if it exists.
        target: Optional[int] = None
        if dict['target'] is not None:
            target = int(dict['target'])

        # Says whether the move successfully happened or was challenged and
        # failed.
        successful = dict['successful']

        return Action(
            action_type=action_type,
            action=action,
            player_id=player_id,
            successful=successful,
            target=target,
        )
