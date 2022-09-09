from typing import Type, Optional, Literal
from random import shuffle

from coup.bots.base_bot import BaseBot
from coup.bots.enums import (
    Character, ActionType, RequestedMove, PrimaryAction, ChallengeAction,
    CounterAction
)
from coup.bots.action import Action
from coup.bots.game_info import GameInfo

from coup.engine.player import Player


NUMBER_OF_PLAYERS = 5
CARD_TO_PRIMARY_ACTION: dict[Character, Optional[PrimaryAction]] = {
    Character.Duke: PrimaryAction.Tax,
    Character.Assassin: PrimaryAction.Assassinate,
    Character.Ambassador: PrimaryAction.Exchange,
    Character.Captain: PrimaryAction.Steal,
    Character.Contessa: None,
}
CARD_TO_COUNTER_ACTION: dict[Character, Optional[CounterAction]] = {
    Character.Duke: CounterAction.BlockForeignAid,
    Character.Assassin: None,
    Character.Ambassador: CounterAction.BlockStealingAsCaptain,
    Character.Captain: CounterAction.BlockStealingAsAmbassador,
    Character.Contessa: CounterAction.BlockAssassination,
}


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
        Runs a turn, but doesn't actually apply the primary action.
        """

        self.history.append({})

        self.run_primary_action(primary_player_id)

        primary_challenged_by = self.run_challenge(
            primary_player_id,
            ActionType.ChallengePrimaryAction
        )

        # TODO: Resolve challenge
        if primary_challenged_by is not None:
            self.run_challenge_response(
                primary_player_id=primary_player_id,
                challenging_player_id=primary_challenged_by,
                action_type=ActionType.ChallengePrimaryAction,
            )

        # TODO: Counter action.

        secondary_challenged_by = self.run_challenge(
            primary_player_id,
            ActionType.ChallengeCounterAction
        )

        # TODO: Resolve challenge.

    def run_primary_action(self, primary_player_id: int) -> None:
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

        action = Action(
            action_type=ActionType.PrimaryAction,
            action=primary_action,
            player_id=primary_player_id,
            successful=None,
            target=target,
        )

        self.history[-1][ActionType.PrimaryAction] = action

    def run_challenge(
        self,
        primary_player_id: int,
        action_type: (
            Literal[ActionType.ChallengePrimaryAction]
            | Literal[ActionType.ChallengeCounterAction]
        )
    ) -> Optional[int]:
        """
        Returns the id of the player that challenged, or None if nobody did.
        """

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
        primary_player_id: int,
        challenging_player_id: int,
        action_type: (
            Literal[ActionType.ChallengePrimaryAction]
            | Literal[ActionType.ChallengeCounterAction]
        )
    ) -> None:
        player = self.players[primary_player_id]
        game_info = GameInfo(
            requested_move=RequestedMove.ChallengeResponse,
            player_id=primary_player_id,
            balances=self.balances,
            own_cards=player.hand,
            revealed_cards=self.revealed_cards,
            players_cards_num=self.players_cards_num,
            history=self.history,
            current_primary_player_id=primary_player_id,
        )
        player.bot.game_info = game_info

        card_to_reveal = player.bot.challenge_response_handler()

        revealed_card = player.hand.pop()

        if action_type == ActionType.ChallengePrimaryAction:
            primary_action = self.history[-1][ActionType.PrimaryAction].action
            allowed = primary_action == CARD_TO_PRIMARY_ACTION[revealed_card]
        elif action_type == ActionType.ChallengeCounterAction:
            counter_action = self.history[-1][ActionType.CounterAction].action
            allowed = counter_action == CARD_TO_COUNTER_ACTION[revealed_card]
        else:
            raise ValueError(f'Unexpected action_type {action_type}')

        # TODO: Finish this.

        if allowed:
            # The original player was telling the truth.

            self.run_influence_loss(
                player_id=challenging_player_id,
                primary_player_id=primary_player_id
            )

        else:
            # The original player was lying.

            self.run_influence_loss(
                player_id=challenging_player_id,
                primary_player_id=primary_player_id
            )

        if len(player.hand) == 0:
            player.eliminated = True

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

        revealed_card = player.hand.pop(card_to_loose_index)
        self.revealed_cards[revealed_card] += 1

        if len(player.hand) == 0:
            player.eliminated = True
