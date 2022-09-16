from coup.tree.game_tree_node import GameTreeNode
from coup.tree.challenge_node import ChallengeNode
from coup.bots.game_info import Player
from coup.bots.enums import Character

"""END LOCAL IMPORTS"""


class PrimaryActionNode(GameTreeNode):
    def generate_children(
        self,
        to_depth: int,
        current_depth: int = 0,
    ):
        if current_depth == to_depth:
            return
        
        self.children = []        
