from coup.common.rules import NUMBER_OF_PLAYERS

from coup.tree.game_tree_node import GameTreeNode

"""END LOCAL IMPORTS"""

from dataclasses import dataclass


@dataclass(kw_only=True)
class GameEndNode(GameTreeNode):
    winning_player_id: int

    def generate_tree(
        self,
        *,
        to_depth: int,
        current_depth: int = 0
    ) -> None:
        """
        This is a terminal node, there are no child states. The tree is already
        generated.
        """

        return

    def evaluate(self) -> tuple[list[float], bool]:
        """
        Gives the winning player a score of 1, and every other player a score
        of 0.
        """

        score: list[float] = [0] * NUMBER_OF_PLAYERS

        score[self.winning_player_id] = 1

        self.evaluation = score, False
        return self.evaluation
