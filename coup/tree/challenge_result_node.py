from coup.tree.game_tree_node import NonPrimaryNode, GameTreeNode
from coup.bots.enums import Character

"""END LOCAL IMPORTS"""

from dataclasses import dataclass


@dataclass
class ChallengeResultNode(NonPrimaryNode):
    challenged_player_id: int
    challenging_player_id: int
    claimed_card: Character

    def _generate_children_for_player_loosing_card(
        self,
        *,
        player_id: int
    ) -> list[GameTreeNode]:
        """
        Generate children for a particular player loosing a card.
        """

        

    def _generate_own_children(self) -> list[GameTreeNode]:
        # Make a child for each player that could loose, for each card they
        # could reveal. Some of these will be impossible, so they are just
        # filled with a plain GameTreeNode, and will hence error if they are
        # evaluated or expanded. I have to put something in there so that the
        # children are in a fixed arrangement for evaluation.

        if self.children is not None:
            return self.children

        unknown_card_counts = self._get_unknown_card_counts()

        self.children = []

        if self.challenged_player_id == self.perspective_player_id:
            # We have one child for each of the card types that could be
            # revealed.
            for card in set(self.perspective_hand):
                if card == self.claimed_card:


        for loosing_player_id in (
            self.challenged_player_id,
            self.challenging_player_id,
        ):
            for character in Character:
                if unknown_card_counts[character] == 0:
                    self.children.append(
                        GameTreeNode(
                            players=self.players,
                            revealed_cards=self.revealed_cards,
                            primary_player_id=self.primary_player_id,
                            perspective_player_id=self.perspective_player_id,
                            perspective_hand=self.perspective_hand
                        )
                    )
