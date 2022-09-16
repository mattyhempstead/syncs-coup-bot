from coup.tree.primary_action_node import PrimaryActionNode
from coup.bots.enums import Character
from coup.bots.game_info import Player
from coup.common.rules import NUMBER_OF_PLAYERS

"""END LOCAL IMPORTS"""


def make_game_root(
    hand: list[Character]
) -> PrimaryActionNode:
    """
    Creates the root node of a game for a player starting with the given id,
    and with the given hand.
    """

    if len(hand) != 2:
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
        hand=hand
    )
