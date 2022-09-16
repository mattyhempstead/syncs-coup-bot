from coup.tree.primary_action_node import PrimaryActionNode
from coup.bots.enums import Character
from coup.bots.game_info import Player
from coup.common.rules import NUMBER_OF_PLAYERS

"""END LOCAL IMPORTS"""


def make_game_root(
    perspective_player_id: int,
    perspective_player_hand: list[Character],
) -> PrimaryActionNode:
    """
    Creates the root node of a game tree from the perspective of the player
    with the given id and the given hand.
    """

    if len(perspective_player_hand) != 2:
        raise ValueError('Expected a hand of two cards.')

    players: list[Player] = []
    for player_id in range(NUMBER_OF_PLAYERS):
        players.append(Player(
            player_id=player_id,
            balance=2,
            card_num=2,
            is_current=False,  # I'm not using is_current at all here.
        ))

    return PrimaryActionNode(
        players=players,
        revealed_cards={},
        primary_player_id=0,
        perspective_player_id=perspective_player_id,
        perspective_hand=perspective_player_hand,
    )
