from typing import Type, Optional, Literal
from random import shuffle

from coup.bots.base_bot import BaseBot
from coup.bots.enums import (
    Character, ActionType, RequestedMove, PrimaryAction, ChallengeAction,
    CounterAction
)
from coup.bots.action import Action
from coup.bots.game_info import GameInfo

from coup.common.rules import (
    NUMBER_OF_PLAYERS, PRIMARY_ACTION_TO_CARD, COUNTER_ACTION_TO_CARD,
    PRIMARY_ACTION_TO_COST, PRIMARY_ACTION_TO_COUNTER_ACTIONS
)

from coup.engine.player import Player


class Engine:
    def __init__(self, bot_classes: list[Type[BaseBot]]) -> None:
        if len(bot_classes) != NUMBER_OF_PLAYERS:
            raise ValueError(
                f'Requires {NUMBER_OF_PLAYERS} competitors got '
                f'{len(bot_classes)}'
            )

        self.deck: list[Character] = (
            [Character.Duke] * 3 +
            [Character.Assassin] * 3 +
            [Character.Ambassador] * 3 +
            [Character.Captain] * 3 +
            [Character.Contessa] * 3
        )
        shuffle(self.deck)

        self.players: list[Player] = []
        for bot_class in bot_classes:
            hand = [self.deck.pop(), self.deck.pop()]
            self.players.append(Player(bot_class(), hand))

        self.revealed_cards: dict[Character, int] = {
            Character.Duke: 0,
            Character.Assassin: 0,
            Character.Ambassador: 0,
            Character.Captain: 0,
            Character.Contessa: 0,
        }

        self.history: list[dict[ActionType, Action]] = []

    def next_player(self, current_player: int) -> int:
        player_id = current_player
        iterated = 0
        while self.players[player_id].eliminated:
            player_id = (player_id + 1) % NUMBER_OF_PLAYERS
            iterated += 1

            if iterated > NUMBER_OF_PLAYERS:
                raise Exception('All players eliminated')

        return player_id

    @property
    def balances(self) -> list[int]:
        return [player.balance for player in self.players]

    @property
    def players_cards_num(self) -> list[int]:
        return [len(player.hand) for player in self.players]

    def draw_card(self) -> Character:
        # The draw is always completely random, there is no preserved order.
        shuffle(self.deck)
        return self.deck.pop()

    def run_game(self) -> None:
        turn = 0
        primary_player_id = 0
        while True:
            self.run_turn_without_primary_resolution(primary_player_id)

            # TODO: Resolve primary action.

            turn += 1
            primary_player_id = self.next_player(primary_player_id)

    def run_turn_without_primary_resolution(
        self,
        primary_player_id: int
    ) -> None:
        """
        Runs a turn, but doesn't actually apply the primary action or eliminate
        players that are reduced to zero influence (hand size). Any resolution
        to challenges and counter actions is applied. As the cost of a primary
        action is charged regardless of whether or not it succeeds, this does
        charge for it, but the actual standard effects of the action will need
        to be resolved later.

        This history, including the success state of all actions, will be
        updated to their final values by this method.
        """

        self.history.append({})
        turn = self.history[-1]

        primary_action, target = self.run_primary_action(primary_player_id)

        primary_challenger_id = None
        if primary_action in PRIMARY_ACTION_TO_CARD:
            # Only allow a challenge if the primary action taken corresponds to
            # a card.
            primary_challenger_id = self.run_challenge(
                target=target,
                primary_player_id=primary_player_id,
                action_type=ActionType.ChallengePrimaryAction,
            )

        if primary_challenger_id is not None:
            # If someone challenged, we run a challenge response.
    
            if self.run_challenge_response(
                challenged_player_id=primary_player_id,
                challenging_player_id=primary_challenger_id,
                primary_player_id=primary_player_id,
                action_type=ActionType.ChallengePrimaryAction,
            ):
                # If the challenge is successful, the primary action fails and
                # the turn is over.

                turn[ActionType.PrimaryAction].successful = False
                turn[ActionType.ChallengePrimaryAction].successful = True
                return
            
            # Otherwise, the challenge fails, and the turn continues.
            turn[ActionType.ChallengePrimaryAction].successful = False

        if len(PRIMARY_ACTION_TO_COUNTER_ACTIONS[primary_action]) == 0:
            # There are no possible counter actions, so the primary action goes
            # ahead and the turn is done.

            turn[ActionType.PrimaryAction].successful = True
            return
        
        # Otherwise, we still need to run the counter action and any challenges
        # to the counter action.

        # TODO: Resolve challenge.
        counter_challenger_id = self.run_challenge(
            target=None,
            primary_player_id=primary_player_id,
            action_type=ActionType.ChallengeCounterAction,
        )

        # TODO: Ensure history is correct.

    def run_primary_action(
        self,
        primary_player_id: int
    ) -> tuple[PrimaryAction, Optional[int]]:
        """
        Returns the PrimaryAction taken and its target, for ease of checking if
        challenges / counter actions are allowed.
        """

        player = self.players[primary_player_id]
        game_info = GameInfo(
            requested_move=RequestedMove.PrimaryAction,
            player_id=primary_player_id,
            balances=self.balances,
            own_cards=player.hand,
            revealed_cards=self.revealed_cards,
            players_cards_num=self.players_cards_num,
            history=self.history,
            current_primary_player_id=primary_player_id,
        )
        player.bot.game_info = game_info

        primary_action, target = player.bot.primary_action_handler()

        # Charge the cost of the action, because they pay this regardless of
        # their success.
        if player.balance < PRIMARY_ACTION_TO_COST[primary_action]:
            raise Exception(
                f'Player {primary_player_id} does not have enough coins to '
                f'take the primary action {primary_action}'
            )
        player.balance -= PRIMARY_ACTION_TO_COST[primary_action]

        action = Action(
            action_type=ActionType.PrimaryAction,
            action=primary_action,
            player_id=primary_player_id,
            successful=None,
            target=target,
        )

        self.history[-1][ActionType.PrimaryAction] = action

        return primary_action, target

    def run_challenge(
        self,
        target: Optional[int],
        primary_player_id: int,
        action_type: (
            Literal[ActionType.ChallengePrimaryAction]
            | Literal[ActionType.ChallengeCounterAction]
        )
    ) -> Optional[int]:
        """
        Returns the id of the player that challenged, or None if nobody did.

        If the action the challenge is being offered for targetted a player,
        only that player may choose to challenge.
        """

        if target is not None:
            if self.run_single_challenge(
                target,
                primary_player_id,
                action_type
            ):
                # The target player did challenge.
                return target

            # The target player did not challenge, and targetted actions cannot
            # be challenged by other players.
            return None

        challenge_player_id = self.next_player(primary_player_id)
        while challenge_player_id != primary_player_id:
            if self.run_single_challenge(
                player_id=challenge_player_id,
                primary_player_id=primary_player_id,
                action_type=action_type,
            ):
                return challenge_player_id

            challenge_player_id = self.next_player(primary_player_id)

        return None

    def run_single_challenge(
        self,
        player_id: int,
        primary_player_id: int,
        action_type: (
            Literal[ActionType.ChallengePrimaryAction]
            | Literal[ActionType.ChallengeCounterAction]
        )
    ) -> bool:
        """
        Returns True if a challenge is made.
        """

        player = self.players[player_id]
        game_info = GameInfo(
            requested_move=RequestedMove.ChallengeAction,
            player_id=player_id,
            balances=self.balances,
            own_cards=player.hand,
            revealed_cards=self.revealed_cards,
            players_cards_num=self.players_cards_num,
            history=self.history,
            current_primary_player_id=primary_player_id,
        )
        player.bot.game_info = game_info

        challenge_action = player.bot.challenge_action_handler()

        action = Action(
            action_type=action_type,
            action=challenge_action,
            player_id=player_id,
            successful=None,
        )

        self.history[-1][ActionType.PrimaryAction] = action

        return challenge_action == ChallengeAction.Challenge

    def run_challenge_response(
        self,
        challenged_player_id: int,
        challenging_player_id: int,
        primary_player_id: int,
        action_type: (
            Literal[ActionType.ChallengePrimaryAction]
            | Literal[ActionType.ChallengeCounterAction]
        )
    ) -> bool:
        """
        Returns whether or not the challenge was successful, to help in the
        setting of history. Does not set history directly.
        """

        challenged_player = self.players[challenged_player_id]
        game_info = GameInfo(
            requested_move=RequestedMove.ChallengeResponse,
            player_id=challenged_player_id,
            balances=self.balances,
            own_cards=challenged_player.hand,
            revealed_cards=self.revealed_cards,
            players_cards_num=self.players_cards_num,
            history=self.history,
            current_primary_player_id=primary_player_id,
        )
        challenged_player.bot.game_info = game_info

        card_to_reveal = challenged_player.bot.challenge_response_handler()

        # Note that this will make their hand look 1 card smaller than it
        # should be (which may causes the challenged_player to temporarily look
        # eliminated).
        revealed_card = challenged_player.hand.pop()

        if action_type == ActionType.ChallengePrimaryAction:
            primary_action = self.history[-1][ActionType.PrimaryAction].action
            if not isinstance(primary_action, PrimaryAction):
                raise TypeError('Expected PrimaryAction')

            allowed = PRIMARY_ACTION_TO_CARD[primary_action] == revealed_card

        elif action_type == ActionType.ChallengeCounterAction:
            counter_action = self.history[-1][ActionType.CounterAction].action
            if not isinstance(counter_action, CounterAction):
                raise TypeError('Expected CounterAction')

            allowed = COUNTER_ACTION_TO_CARD[counter_action] == revealed_card

        else:
            raise ValueError(f'Unexpected action_type {action_type}')

        if allowed:
            # The challenged player was telling the truth, challenging player
            # looses a card.

            self.run_influence_loss(
                player_id=challenging_player_id,
                primary_player_id=primary_player_id
            )

            # The challenged player returns their card to the draw deck, and
            # then draws a new one.

            self.deck.append(revealed_card)
            challenged_player.hand.append(self.draw_card())

            # The challenge was unsuccessful.
            return False

        # Otherwise, the challenged player was lying, and they just don't get
        # back the card they revealed.

        # TODO: Check if this is the case, or if they are instead issued
        # with a choice of what to discard. If that is the case, then the
        # "revealed card" shouldn't be popped from their hand.

        # The challenge was successful.
        return True

    def run_influence_loss(
        self,
        player_id: int,
        primary_player_id: int,
    ) -> None:
        player = self.players[player_id]
        game_info = GameInfo(
            requested_move=RequestedMove.ChallengeResponse,
            player_id=player_id,
            balances=self.balances,
            own_cards=player.hand,
            revealed_cards=self.revealed_cards,
            players_cards_num=self.players_cards_num,
            history=self.history,
            current_primary_player_id=primary_player_id,
        )
        player.bot.game_info = game_info

        card_to_loose_index = player.bot.discard_choice_handler()

        if card_to_loose_index < 0 or card_to_loose_index >= len(player.hand):
            raise Exception(
                f'Player {player_id} with hand of size {len(player.hand)} '
                'gave invalid discard choice of card with index '
                f'{card_to_loose_index}'
            )

        revealed_card = player.hand.pop(card_to_loose_index)
        self.revealed_cards[revealed_card] += 1

    def run_counter_action(
        self,
        primary_player_id: int
    ):
        pass
