from coup.tree.game_tree_node import GameTreeNode, MultipleDeciderNode
from coup.tree.challenge_result_node import ChallengeResultNode

from coup.bots.enums import Character

"""END LOCAL IMPORTS"""

from dataclasses import dataclass


@dataclass(kw_only=True)
class ChallengeNode(MultipleDeciderNode):
    challenging_primary_action: bool
    claimed_card: Character

    def _generate_own_children(self) -> list[GameTreeNode]:
        if self.children is not None:
            return self.children

        # The children must created in the strict order of a multiple decider
        # node. They must be first one corresponding to each of the players
        # that can make the decision in the order they make the decision, and
        # then one corresponding to no player making the decision.

        self.children = []

        # Add the children for each player that can make the decision.
        current_player_id = self._next_player_id(
            starting_player_id=self.subject_player_id
        )
        while current_player_id != self.subject_player_id:
            self.children.append(
                ChallengeResultNode(
                    players=self.players,
                    revealed_cards=self.revealed_cards,
                    primary_player_id=self.primary_player_id,
                    perspective_player_id=self.perspective_player_id,
                    perspective_hand=self.perspective_hand,

                    challenged_player_id=self.subject_player_id,
                    claimed_card=self.claimed_card,
                    unresolved_primary_action=self.unresolved_primary_action,
                    unresolved_primary_action_target_id=self.unresolved_primary_action_target_id,  # nopep8

                    challenging_player_id=current_player_id,
                )
            )

            current_player_id = self._next_player_id(
                starting_player_id=current_player_id
            )

        # Add the child for no player making the decision.

        # TODO: This.

        return self.children
