from coup.bots.enums import *
from coup.bots.action import Action

"""END LOCAL IMPORTS"""

from typing import Dict, List, Optional
from dataclasses import dataclass


class Player:
    def __init__(self, player_id, balance, card_num, current):
        self.player_id:int = player_id
        self.balance:int = balance
        self.card_num:int = card_num

        self.is_current:bool = is_current

    @property
    def alive(self) -> bool:
        return self.card_num > 0

    @property
    def dead(self) -> bool:
        return self.card_num == 0


class GameInfo:
    PLAYER_NUM = 5

    def __init__(
        self,
        requested_move: RequestedMove,
        player_id: int,
        balances: list[int],
        own_cards: list[Character],
        players_cards_num: list[int],
        revealed_cards: dict[Character, int],
        history: list[dict[ActionType, Action]],
        current_primary_player_id: int,
    ) -> None:
        self.requested_move = requested_move
        self.player_id = player_id
        self.balances = balances
        self.own_cards = own_cards
        self.players_cards_num = players_cards_num
        self.revealed_cards = revealed_cards
        self.history = history
        self.current_primary_player_id = current_primary_player_id

        self.players = []
        for i in range(GameInfo.PLAYER_NUM):
            p = Player(
                player_id = self.player_id,
                balance = self.balances[self.player_id],
                card_num = self.players_cards_num[self.player_id],
                current = (i==self.player_id),
            )
            self.players.append(p)

        self.current_player = self.players[self.player_id]
        self.current_primary_player = self.players[self.current_primary_player_id]

    @staticmethod
    def from_dictionary(dict) -> 'GameInfo':
        # The move currently requested from you.
        requested_move: RequestedMove = RequestedMove(int(dict['requested_move']))

        # Your player id
        player_id: int = int(dict['player_id'])

        # A list of integers where the integers refer to the current balance of
        # each player. For example, balance[1] refers to the number of coins that
        # player 1 has currently.
        balances: List[int] = [int(x) for x in dict['balances']]

        # A list of Characters representing your current cards. See Character enum for details.
        own_cards: List[Character] = [Character(int(x)) for x in dict['own_cards']]

        # A list of integers where the integers refer to the current number of
        # cards each player possesses. For example, other_players_cards_num[2] refers
        # to the number of cards player 2 has currently.
        players_cards_num: List[int] = [int(x) for x in dict['players_cards_num']]

        # A dictionary index by Character containing an integer. This integer
        # refers to the number of that Character card that has been revealed
        # thus far. Hint: you can figure out which player revealed each card
        # by parsing the history.
        revealed_cards: Dict[Character, int] = {Character(int(character)):int(num) for (character, num) in dict['revealed_cards'].items()}

        # A list of turns. Each turn is a dictionary keyed by the action type in that turn.
        # The value is an Action which contains the move made & all relevant information.
        history: List[Dict[ActionType, Action]] = [{ActionType(int(move['action_type'])):Action.from_dictionary(move['action']) for move in turn['turn']} for turn in dict['history']]

        # An integer representing the player who played/is playing the current
        # primary action. Note: this can be you. 
        current_primary_player_id: int = int(dict['current_primary_player'])

        return GameInfo(
            requested_move=requested_move,
            player_id=player_id,
            balances=balances,
            own_cards=own_cards,
            players_cards_num=players_cards_num,
            revealed_cards=revealed_cards,
            history=history,
            current_primary_player_id=current_primary_player_id,
        )

    def get_next_alive_player(self) -> Player:
        next_alive = (self.player_id + 1) % 5
        while self.players_cards_num[next_alive] == 0:
            next_alive = (next_alive + 1) % 5

        return self.players[next_alive]

    def get_richest_player(self) -> Player:
        """ 
        Returns the richest alive player (not including current / self player).
        If multiple richest will return the first in turn order.
        """
        richest_p = None
        for p in self.players:
            if p.is_current or p.dead:
                continue

            if richest_p is None or p.balance > richest_p.balance:
                richest_p = p

        return richest_p
