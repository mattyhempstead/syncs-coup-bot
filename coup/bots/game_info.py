from coup.bots.enums import *
from coup.bots.action import Action
from coup.common.rules import *


"""END LOCAL IMPORTS"""

from typing import Dict, List, Optional
from dataclasses import dataclass


class Player:
    def __init__(
        self,
        player_id: int,
        balance: int,
        card_num: int,
        is_current: bool
    ):
        self.player_id = player_id
        self.balance = balance
        self.card_num = card_num

        self.is_current = is_current

    @property
    def alive(self) -> bool:
        return self.card_num > 0

    @property
    def dead(self) -> bool:
        return self.card_num == 0

    def __repr__(self) -> str:
        return f"<Player id={self.player_id}, bal={self.balance}, cn={self.card_num}>"


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
                player_id = i,
                balance = self.balances[i],
                card_num = self.players_cards_num[i],
                is_current = (i==self.player_id),
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


    @property
    def turn(self) -> int:
        """ The turn number starting at 0 """
        # A history of length 1 implies the first turn of the game.
        return len(self.history)-1

    @property
    def remaining_players(self) -> int:
        return len([p for p in self.players if not p.is_current and p.alive])

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
            if p.is_current or p.dead: continue
            if richest_p is None or p.balance > richest_p.balance:
                richest_p = p
        return richest_p

    def get_most_cards(self) -> int:
        """ Returns the number of cards owned by the best non-self player """
        return max([p.card_num for p in self.players if not p.is_current])

    def get_winning_player_order(self) -> List[Player]:
        """ 
        Returns a list of alive (non-self) players ordered by card number desc then coins desc.
        """
        most_cards = self.get_most_cards()
        players = [p for p in self.players if not p.is_current and p.alive]
        players.sort(key=lambda p: (p.card_num, p.balance), reverse=True)
        return players

    def get_winning_player(self) -> Player:
        """ 
        Returns the first (non-self) player ordered by card number desc then coins desc.
        """
        return self.get_winning_player_order()[0]

    def get_history_primary_action(self):
        """ Returns the Action object from history of the PrimaryAction assuming one exists """
        if ActionType.PrimaryAction not in self.history[-1]:
            raise Exception("History contains no PrimaryAction (we must presumably be in a PrimaryMove state?)")

        action:Action = self.history[-1][ActionType.PrimaryAction]
        return action

    def get_history_counter_action(self):
        """ Returns the Action object from history of the CounterAction assuming one exists """
        if ActionType.CounterAction not in self.history[-1]:
            raise Exception("History contains no CounterAction")

        action:Action = self.history[-1][ActionType.CounterAction]
        return action


    def exists_historical_counter(
        self,
        counter_action_type:CounterAction,
        player_id:Optional[int]=None,
        alive:bool=False,  # whether we exclude players that are eliminated
    ) -> bool:
        """
            Returns whether a specific CounterAction type has been successfully applied in the past.
            (Not including counters that we applied).

            Useful if we want to check, for example, whether any other player is willing to block ForeignAid.
        """
        for h in self.history[:-1]:
            # Skip if no counteraction
            if ActionType.CounterAction not in h: continue 

            counter_action = h[ActionType.CounterAction]

            # Skip it wrong type
            if counter_action.action != counter_action_type: continue 

            # Skip if not successful
            if counter_action.successful == False: continue

            # Skip if it was us
            if counter_action.player_id == self.player_id: continue

            # Skip if not specified target player
            if player_id is not None and counter_action.player_id != player_id: continue

            # Exclude counters from eliminated players
            if alive and self.players[counter_action.player_id].dead: continue

            return True
        
        return False


    def get_character_location(self, character:Character) -> int:
        """ Returns location of a given owned character. """
        if character not in self.own_cards:
            raise Exception("Character is not owned by us")
        
        if len(self.own_cards) == 2 and self.own_cards[1] == character:
            return 1
        else:
            return 0


    def get_winning_player_without_counter(self, counter_action_type:CounterAction) -> Optional[Player]:
        """
            Return a list of players in order of winningness who have not historically performed a
            particular counter.

            This is not entirely accurate since we should really be ignoring people that have done
            the counteraction but then proceeded to do an exchange or give that card up in a challenge.
        """
        winner_players = self.get_winning_player_order()
        winner_players_without_counter = list(filter(
            lambda p: not self.exists_historical_counter(counter_action_type, p.player_id),
            winner_players
        ))

        # If all alive players have countered return None
        # This will often be true especially in endgame
        if len(winner_players_without_counter) == 0:
            return None

        return winner_players_without_counter[0]



    @property
    def known_cards(self) -> dict[Character, int]:
        """
            A dict counting all the known cards.

            This is currently based on the revealed_cards dict and own_cards.
            Could additionally have temp values based on recent exchanges or challenges.    

            Also, if we decide certain players are being honest with heuristics, we can 
            accumulate more predictions of what cards are held in other players hands
            and cross reference with the player performing the action. Of course we can't
            be certain but as long as the alternative of not making any assumptions is 
            statistically worse we might as well make the heuristic.
        """
        known_cards = self.revealed_cards.copy()
        for c in self.own_cards:
            if c not in known_cards:
                known_cards[c] = 0
            known_cards[c] += 1
        return known_cards


    def is_lying(self):
        """ Return true if most recent move is definitely lying (whether a primary or counter) """
        h = self.history[-1]

        if ActionType.CounterAction in h:
            action = h[ActionType.CounterAction]
            action_card = COUNTER_ACTION_TO_CARD[action.action]
        elif ActionType.PrimaryAction in h:
            action = h[ActionType.PrimaryAction]
            action_card = PRIMARY_ACTION_TO_CARD[action.action]

        if action.player_id == self.current_player.player_id:
            raise Exception("We made the move???")

        # Check known cards to determine whether they are certainly lying
        known_cards = self.known_cards
        if action_card in known_cards and known_cards[action_card] == 3:
            return True

        return False
