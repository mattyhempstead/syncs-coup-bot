from more_itertools import first
from coup.tree.game_tree_node import DeciderNode, GameTreeNode
from coup.tree.challenge_node import ChallengeNode

from coup.bots.enums import PrimaryAction

from coup.common.rules import PRIMARY_ACTION_HAS_TARGET, PRIMARY_ACTION_TO_CARD


"""END LOCAL IMPORTS"""


class PrimaryActionNode(DeciderNode):
    def _generate_own_children(self,) -> list[GameTreeNode]:
        if self.children is not None:
            return self.children

        self.children = []

        for primary_action in PrimaryAction:
            if not PRIMARY_ACTION_HAS_TARGET[primary_action]:
                self.children.append(
                    ChallengeNode(
                        players=self.players,
                        revealed_cards=self.revealed_cards,
                        primary_player_id=self.primary_player_id,
                        perspective_player_id=self.perspective_player_id,
                        perspective_hand=self.perspective_hand,

                        unresolved_primary_action=primary_action,
                        unresolved_primary_action_target_id=None,
                        subject_player_id=self.primary_player_id,
                        claimed_card=PRIMARY_ACTION_TO_CARD[primary_action],
                        challenging_primary_action=True,
                    )
                )

                continue

            target_id = self._next_player_id(
                starting_player_id=self.primary_player_id
            )
            while target_id != self.primary_player_id:
                self.children.append(
                    ChallengeNode(
                        players=self.players,
                        revealed_cards=self.revealed_cards,
                        primary_player_id=self.primary_player_id,
                        perspective_player_id=self.perspective_player_id,
                        perspective_hand=self.perspective_hand,

                        unresolved_primary_action=primary_action,
                        unresolved_primary_action_target_id=target_id,
                        subject_player_id=self.primary_player_id,
                        claimed_card=PRIMARY_ACTION_TO_CARD[primary_action],
                        challenging_primary_action=True
                    )
                )

                target_id = self._next_player_id(
                    starting_player_id=target_id
                )

        return self.children
