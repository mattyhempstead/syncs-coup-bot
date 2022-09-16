from coup.tree.primary_action_node import PrimaryActionNode
from coup.bots.enums import Character, PrimaryAction
from coup.bots.game_info import Player
from coup.common.rules import NUMBER_OF_PLAYERS

"""END LOCAL IMPORTS"""

from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class GameTreeNode:
    players: list[Player]
    revealed_cards: dict[Character, int]
    primary_player_id: int
    perspective_player_id: int
    perspective_hand: list[Character]
    children: Optional[list['GameTreeNode']] = None
    # TODO: Maybe track history here.
    # TODO: Maybe track the current turn here.
    # TODO: Maybe track the number of cards in the deck here.

    def generate_children(
        self,
        to_depth: int,
        current_depth: int = 0
    ) -> list['GameTreeNode']:
        """
        Populate the children property of this node. Also populate the children
        of all of its descendants to a depth of to_depth.
        """

        raise NotImplemented

    def next_player_id(self, starting_player_id: int) -> int:
        testing_player_id = (starting_player_id + 1) % NUMBER_OF_PLAYERS
        iterated = 0

        while self.players[testing_player_id].dead:
            testing_player_id = (testing_player_id + 1) % NUMBER_OF_PLAYERS
            iterated += 1

            if iterated > NUMBER_OF_PLAYERS:
                raise Exception('All players eliminated')

        return testing_player_id

    def subtree_size(self) -> int:
        if self.children is None:
            return 1

        return sum(child.subtree_size() for child in self.children)


@dataclass(kw_only=True)
class NonPrimaryGameTreeNode(GameTreeNode):
    unresolved_primary_action: PrimaryAction
    unresolved_target: Optional[int]

    def make_next_turn_node(self) -> PrimaryActionNode:
        """
        Create the PrimaryActionNode with state corresponding to the state of
        this node with the unresolved primary action resolved.
        """

        players = [*self.players]
        perspective_hand = [*self.perspective_hand]

        match self.unresolved_primary_action:
            case PrimaryAction.Income:
                players[self.primary_player_id] = Player(
                    self.primary_player_id,
                    self.players[self.primary_player_id].balance + 1,
                    self.players[self.primary_player_id].card_num,
                    False
                )

            case PrimaryAction.ForeignAid:
                players[self.primary_player_id] = Player(
                    self.primary_player_id,
                    self.players[self.primary_player_id].balance + 1,
                    self.players[self.primary_player_id].card_num,
                    False
                )

            case PrimaryAction.Coup:
                pass

            case PrimaryAction.Tax:
                pass

            case PrimaryAction.Assassinate:
                pass

            case PrimaryAction.Exchange:
                pass

            case PrimaryAction.Steal:
                pass

            case other:
                raise ValueError(
                    'Unknown unresolved primary action '
                    f'{self.unresolved_primary_action}'
                )

        return PrimaryActionNode(
            players=players,
            revealed_cards=self.revealed_cards,
            primary_player_id=self.next_player_id(self.primary_player_id),
            perspective_player_id=self.perspective_player_id,
            perspective_hand=perspective_hand
        )
