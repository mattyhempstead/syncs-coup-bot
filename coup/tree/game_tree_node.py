from coup.bots.enums import Character, PrimaryAction
from coup.bots.game_info import Player
from coup.common.rules import NUMBER_OF_PLAYERS

"""END LOCAL IMPORTS"""

from dataclasses import dataclass
from typing import Optional
from fractions import Fraction


# Parameters describing the relative weighting of the importance of cards to
# the importance of coins in the heuristic.
HEURISTIC_CARD_WEIGHT = 0.9
HEURISTIC_BALANCE_WEIGHT = 1 - HEURISTIC_CARD_WEIGHT


@dataclass(kw_only=True)
class GameTreeNode:
    players: list[Player]
    revealed_cards: dict[Character, int]

    # The player who is making the primary action.
    primary_player_id: int

    perspective_player_id: int
    # This slightly duplicates the card_num of the perspective player in the
    # players list. I'll just have to try to keep both updated.
    perspective_hand: list[Character]

    # None unless the children have been generated.
    children: Optional[list['GameTreeNode']] = None

    # None unless an evaluation has been done. The boolean is true if the
    # evaluation involved a heuristic.
    evaluation: Optional[tuple[list[float], bool]]

    # TODO: Maybe track history here.
    # TODO: Maybe track the current turn here.
    # TODO: Maybe track the number of cards in the deck here.

    @property
    def number_of_remaining_player(self) -> int:
        count = 0

        for player in self.players:
            if player.alive:
                count += 1

        return count

    def generate_children(
        self,
        *,
        to_depth: int,
        current_depth: int = 0
    ) -> None:
        """
        Populate the children property of this node. Also populate the children
        of all of its descendants to a depth of to_depth.
        """

        raise NotImplemented

    def _next_player_id(
        self,
        *,
        starting_player_id: int,
        backwards: int = False
    ) -> int:
        step = -1 if backwards else 1

        testing_player_id = (starting_player_id + step) % NUMBER_OF_PLAYERS
        iterated = 0

        while self.players[testing_player_id].dead:
            testing_player_id = (testing_player_id + step) % NUMBER_OF_PLAYERS
            iterated += 1

            if iterated > NUMBER_OF_PLAYERS:
                raise Exception('All players eliminated')

        return testing_player_id

    def subtree_size(self) -> int:
        if self.children is None:
            return 1

        return sum(child.subtree_size() for child in self.children)

    def _heuristically_evaluate(self) -> list[float]:
        """
        Return a heuristic score of the state of the game in this node for each
        player.
        """

        total_cards = 0
        total_balance = 0
        for player in self.players:
            total_cards += player.card_num
            total_balance += player.balance

        return [
            HEURISTIC_CARD_WEIGHT * (player.card_num / total_cards)
            + HEURISTIC_BALANCE_WEIGHT * (player.balance / total_balance)
            for player in self.players
        ]

    def evaluate(self) -> tuple[list[float], bool]:
        raise NotImplemented

    @staticmethod
    def _best_child_scores_for_player_id(
        *,
        children: list['GameTreeNode'],
        player_id: int,
    ) -> tuple[list[float], bool]:
        """
        Evaluates the given child nodes, and returns the score most favourable
        to the player of the given ID. This is essentially the DeciderNode
        evaluation, but abstracted our so it can also be used by the
        UsuallyStochasticNode when it isn't being stochastic. It is static so
        it doesn't need to rely on the specific properties of either subclass.
        """

        best_for_decider: list[float] = [0] * len(children)
        was_heuristic = False

        for child in children:
            child_scores, child_was_heuristic = child.evaluate()

            # If any child was determined heuristically, the whole thing was,
            # because even if the heuristic value wasn't selected, maybe the
            # true non-heuristic value would have been.
            was_heuristic = was_heuristic or child_was_heuristic

            if (
                child_scores[player_id]
                > best_for_decider[player_id]
            ):
                best_for_decider = child_scores

        return best_for_decider, was_heuristic


@dataclass(kw_only=True)
class DeciderNode(GameTreeNode):
    # The player who picks which of the current actions is to be applied.
    deciding_player_id: int

    def evaluate(self) -> tuple[list[float], bool]:
        """
        Return an evaluation score for the current state, recursively evaluates
        on all non-evaluated and heuristically evaluated nodes. The results are
        stored on the nodes in addition to being returned. The boolean is true
        if the scores were evaluated heuristically.

        In proper minimax style, this assumes that the player who gets to make
        the decision will make the choice that is "best" for them.
        """

        # TODO: Implement pruning.

        if self.evaluation is not None and not self.evaluation[1]:
            return self.evaluation

        if self.children is None:
            self.evaluation = self._heuristically_evaluate(), True
            return self.evaluation

        self.evaluation = GameTreeNode._best_child_scores_for_player_id(
            children=self.children,
            player_id=self.deciding_player_id,
        )
        return self.evaluation


@dataclass(kw_only=True)
class UsuallyStochasticNode(GameTreeNode):
    child_probabilities: Optional[list[Fraction]]
    perspective_player_deciding: bool

    def evaluate(self) -> tuple[list[float], bool]:
        """
        Very much like the evaluation of a DeciderNode, only the score
        because a sum of all of the child scores weighted by probabilities,
        instead of taking the one that is best of the decider, as there is no
        decider.

        _Unless_ the perspective player is deciding, in which case they pick
        like a usual decider node.

        Hence the usually.
        """

        if self.evaluation is not None and not self.evaluation[1]:
            return self.evaluation

        if self.children is None:
            self.evaluation = self._heuristically_evaluate(), True
            return self.evaluation

        if self.perspective_player_deciding:
            self.evaluation = GameTreeNode._best_child_scores_for_player_id(
                children=self.children,
                player_id=self.perspective_player_id,
            )
            return self.evaluation

        if (
            self.child_probabilities is None
            or len(self.child_probabilities) != len(self.children)
            or sum(self.child_probabilities) != 1
        ):
            raise ValueError(
                'Invalid child_probabilities '
                f'{self.child_probabilities}'
            )

        scores: list[float] = [0] * len(self.children)
        was_heuristic = False

        for child in self.children:
            child_scores, child_was_heuristic = child.evaluate()

            was_heuristic = was_heuristic or child_was_heuristic

            for index, score in enumerate(child_scores):
                scores[index] += self.child_probabilities[index] * score

        self.evaluation = scores, was_heuristic
        return self.evaluation


@dataclass(kw_only=True)
class MultipleDeciderNode(GameTreeNode):
    """
    A node for when evaluation depends on the decisions of multiple players in
    an order. For example a ChallengeNode or a CounterActionPlayerNode. A
    player only gets the option to challenge or counter if all previous players
    have declined it.

    This removes the need for a whole sequence of yes / no nodes.
    """

    # The player who gets the first choice as to what happens, if they turn it
    # down the next player in table order may take up the action, and so on.
    first_deciding_player: int

    def evaluate(self) -> tuple[list[float], bool]:
        """
        Output as per DeciderNode.evaluate.

        The children for this node must be in a strict order. The first child
        must correspond to the first player choosing to act, the second to the
        second, and so on. The last child must correspond to no player choosing
        to act.
        """

        if self.evaluation is not None and not self.evaluation[1]:
            return self.evaluation

        if self.children is None:
            self.evaluation = self._heuristically_evaluate(), True
            return self.evaluation

        if len(self.children) != self.number_of_remaining_player + 1:
            raise Exception(f'Invalid number of children {len(self.children)}')

        # We go through the players in reverse order, because to work out if
        # a player should choose to take the action, we need to know what would
        # happen if they did not.

        # Represents the state that will be chosen if all players asked before
        # (before in the actual order, after in the order we are going through)
        # chose not to take the action.
        chosen_so_far, was_heuristic = self.children[-1].evaluate()

        # Iterate through the children in reverse order, updating what would be
        # chosen as we go.
        deciding_player_id = self._next_player_id(
            starting_player_id=self.first_deciding_player,
            backwards=True,
        )
        for child in reversed(self.children[:-1]):
            child_scores, child_was_heuristic = child.evaluate()

            was_heuristic = was_heuristic or child_was_heuristic

            if (
                child_scores[deciding_player_id]
                > chosen_so_far[deciding_player_id]
            ):
                chosen_so_far = child_scores

            deciding_player_id = self._next_player_id(
                starting_player_id=deciding_player_id,
                backwards=True,
            )

        self.evaluation = chosen_so_far, was_heuristic
        return self.evaluation


@dataclass(kw_only=True)
class NonPrimaryNode(GameTreeNode):
    unresolved_primary_action: PrimaryAction
    unresolved_primary_action_target: Optional[int]
    unresolved_primary_action_revealed_card: Optional[Character]
