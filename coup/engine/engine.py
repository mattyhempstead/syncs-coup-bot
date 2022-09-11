from typing import Type, Optional, Literal
from random import shuffle

from coup.bots.bots.base_bot import BaseBot
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
    TIMEOUT_TURN:int = 100  # Number of turns until we timeout the engine

    def __init__(
        self,
        bot_classes: list[Type[BaseBot]],
        debug:bool=True,
        shuffle_players: bool=False
    ) -> None:
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

        if shuffle_players:
            bot_classes = bot_classes.copy()
            shuffle(bot_classes)

        for player_id, bot_class in enumerate(bot_classes):
            self.players.append(
                Player(
                    bot=bot_class(local_mode=True),
                    player_id=player_id,
                    hand=[self.deck.pop(), self.deck.pop()]
                )
            )


        self.revealed_cards: dict[Character, int] = {
            Character.Duke: 0,
            Character.Assassin: 0,
            Character.Ambassador: 0,
            Character.Captain: 0,
            Character.Contessa: 0,
        }

        self.history: list[dict[ActionType, Action]] = []


        # Sorry James, my usage of various class variables and methods is probably quite disagreeable

        self.debug:bool = debug

        self.turn:int = 0
        self.complete:bool = False

        self.eliminated_players:List[Player] = []
        """ A list of players which are appended as they are eliminated """


    def next_player(self, current_player: int) -> int:
        player_id = (current_player + 1) % NUMBER_OF_PLAYERS
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
        
        # Print some stuff about the game
        if self.debug:
            print("Cards dealt:")
            for p in self.players:
                print(p, '-', p.hand)
            print()

        self.turn = 0
        primary_player_id = 0
        while True:
            if self.turn == Engine.TIMEOUT_TURN:
                if self.debug:
                    print(f"Game timed out after {self.turn} turns")
                    break
                break

            if self.debug:
                print(f'Turn {self.turn}.')
                print("Balances:", [p.balance for p in self.players])
                print("Card Nums:", [len(p.hand) for p in self.players])

            primary_action_details = self.run_turn_without_primary_resolution(
                primary_player_id
            )

            if primary_action_details is not None:
                primary_action, target = primary_action_details
                self.resolve_successful_primary_action(
                    primary_player_id=primary_player_id,
                    primary_action=primary_action,
                    target=target
                )

            if ActionType.PrimaryAction in self.history[-1]:
                action = self.history[-1][ActionType.PrimaryAction]
                if self.debug:
                    print(
                        f'PrimaryAction: {self.players[action.player_id]}; action '
                        f'{action.action.name}; target {action.target}; '
                        f'successful {action.successful}.'
                    )
            if ActionType.ChallengePrimaryAction in self.history[-1]:
                action = self.history[-1][ActionType.ChallengePrimaryAction]
                if self.debug:
                    print(
                        f'ChallengePrimaryAction: {self.players[action.player_id]}; '
                        f'action {action.action.name}; successful '
                        f'{action.successful}.'
                    )
            if ActionType.CounterAction in self.history[-1]:
                action = self.history[-1][ActionType.CounterAction]
                if self.debug:
                    print(
                        f'CounterAction: {self.players[action.player_id]}; action '
                        f'{action.action.name}; successful {action.successful}.'
                    )
            if ActionType.ChallengeCounterAction in self.history[-1]:
                action = self.history[-1][ActionType.ChallengeCounterAction]
                if self.debug:
                    print(
                        f'ChallengeCounterAction: {self.players[action.player_id]}; '
                        f'action {action.action.name}; successful '
                        f'{action.successful}.'
                    )

            # Build eliminated_players list
            # This is 100% a terrible way to do this but I'm too scared to insert this anywhere else 
            # without breaking things.
            for p in self.players:
                if p.eliminated and p not in self.eliminated_players:
                    self.eliminated_players.append(p)

            if len(self.remaining_players) == 1:
                if self.debug:
                    print(f'Game over.')
                    print(f'{self.winner} wins.')
                break

            self.turn += 1
            primary_player_id = self.next_player(primary_player_id)

        self.complete = True

    def run_turn_without_primary_resolution(
        self,
        primary_player_id: int
    ) -> Optional[tuple[PrimaryAction, Optional[int]]]:
        """
        Runs a turn, but doesn't actually apply the primary action or eliminate
        players that are reduced to zero influence (hand size). Any resolution
        to challenges and counter actions is applied. As the cost of a primary
        action is charged regardless of whether or not it succeeds, this does
        charge for it, but the actual standard effects of the action will need
        to be resolved later.

        This history, including the success state of all actions, will be
        updated to their final values by this method.

        Returns the PrimaryAction and its target if one was executed
        successfully, otherwise returns None, for ease of resolving it.
        """

        self.history.append({})
        turn = self.history[-1]

        primary_action, target = self.run_primary_action(primary_player_id)

        primary_challenger_id = None
        if primary_action in PRIMARY_ACTION_TO_CARD:
            # Only allow a challenge if the primary action taken corresponds to
            # a card.
            primary_challenger_id = self.run_challenge(
                challenged_player_id=primary_player_id,
                primary_player_id=primary_player_id,
                action_type=ActionType.ChallengePrimaryAction,
            )

        # If someone challenged, we run a challenge response.
        if primary_challenger_id is not None:
            if self.run_challenge_response(
                challenged_player_id=primary_player_id,
                challenging_player_id=primary_challenger_id,
                primary_player_id=primary_player_id,
                action_type=ActionType.ChallengePrimaryAction,
            ):
                # If the challenge is successful, the primary action fails and
                # we are done.

                turn[ActionType.PrimaryAction].successful = False
                turn[ActionType.ChallengePrimaryAction].successful = True

                return None

            # Otherwise, the challenge fails, and the turn continues.
            turn[ActionType.ChallengePrimaryAction].successful = False

        # The PrimaryAction has now survived any challenges.

        if len(PRIMARY_ACTION_TO_COUNTER_ACTIONS[primary_action]) == 0:
            # There are no possible counter actions, so the primary action goes
            # ahead and we are done.

            turn[ActionType.PrimaryAction].successful = True

            return primary_action, target

        # Otherwise, we still need to run the counter action and any challenges
        # to the counter action.

        counterer_id = self.run_counter_action(
            target=target,
            primary_action=primary_action,
            primary_player_id=primary_player_id,
        )

        if counterer_id is None:
            # No counter action was taken, so the primary action goes ahead and
            # we are done.

            turn[ActionType.PrimaryAction].successful = True

            return primary_action, target

        # All counter actions can be challenged, so we always run a challenge.

        counter_challenger_id = self.run_challenge(
            challenged_player_id=counterer_id,
            primary_player_id=primary_player_id,
            action_type=ActionType.ChallengeCounterAction,
        )

        # If the counter action was challenged, we run a challenge response.
        if counter_challenger_id is not None:
            if self.run_challenge_response(
                challenged_player_id=counterer_id,
                challenging_player_id=counter_challenger_id,
                primary_player_id=primary_player_id,
                action_type=ActionType.ChallengeCounterAction
            ):
                # If the challenge was successful, the counter action fails,
                # and so the primary action succeeds, and the turn is over.

                turn[ActionType.ChallengeCounterAction].successful = True
                turn[ActionType.CounterAction].successful = False
                turn[ActionType.PrimaryAction].successful = True

                return primary_action, target

            else:
                # Otherwise, the challenge fails, the counter succeeds, and so
                # the primary action fails. And then the turn is over.

                turn[ActionType.ChallengeCounterAction].successful = False
                turn[ActionType.CounterAction].successful = True
                turn[ActionType.PrimaryAction].successful = False

                return None

        # Otherwise, there was no challenge to the counter action, so the
        # counter action succeeds, so the primary action fails, and we are
        # done.

        turn[ActionType.CounterAction].successful = True
        turn[ActionType.PrimaryAction].successful = False

        return None

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
        challenged_player_id: int,
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

        challenging_player_id = self.next_player(challenged_player_id)
        while challenging_player_id != challenged_player_id:
            if self.run_single_challenge(
                player_id=challenging_player_id,
                primary_player_id=challenged_player_id,
                action_type=action_type,
            ):
                return challenging_player_id

            challenging_player_id = self.next_player(challenging_player_id)

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

        if challenge_action == ChallengeAction.NoChallenge:
            # This player is not issuing a challenge, so we don't need to add
            # anything to the history.
            return False

        # This player is issuing a challenge.

        action = Action(
            action_type=action_type,
            action=challenge_action,
            player_id=player_id,
            successful=None,
        )

        self.history[-1][action_type] = action
        return True

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

    def run_discard(
        self,
        player_id: int,
        primary_player_id: int,
    ) -> Character:
        """
        Returns the discarded character. Note that this does not discard _to_
        anywhere, so should not be used directly. It should be called through
        run_influence_loss (which discards to the revealed cards) or
        run_discard_to_deck (which discards to the deck).
        """

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

        return player.hand.pop(card_to_loose_index)

    def run_influence_loss(
        self,
        player_id: int,
        primary_player_id: int,
    ) -> None:
        player = self.players[player_id]

        if len(player.hand) == 0:
            print(
                'WARNING: run_influence_loss on a player with no cards. Doing '
                'nothing. I believe this is correct behaviour.'
            )

        revealed_card = self.run_discard(
            player_id=player_id,
            primary_player_id=primary_player_id
        )

        self.revealed_cards[revealed_card] += 1

    def run_discard_to_deck(
        self,
        player_id: int,
        primary_player_id: int,
    ) -> None:
        player = self.players[player_id]

        if len(player.hand) == 0:
            print(
                'WARNING: run_discard_to_deck on a player with no cards. '
                'Doing nothing. I believe this is correct behaviour.'
            )

        revealed_card = self.run_discard(
            player_id=player_id,
            primary_player_id=primary_player_id
        )

        self.deck.append(revealed_card)

    def run_counter_action(
        self,
        primary_action: PrimaryAction,
        target: Optional[int],
        primary_player_id: int,
    ) -> Optional[int]:
        """
        If a counter action was taken, returns the id of the player that took
        the counter action. Otherwise returns None.

        Only allows valid counter actions to the primary action, errors on
        players giving invalid counter actions.

        If the primary action being taken has a target, only that player may
        counter.
        """

        if target is not None:
            counter_action = self.run_single_counter_action(
                player_id=target,
                primary_action=primary_action,
                primary_player_id=primary_player_id,
            )

            if counter_action == CounterAction.NoCounterAction:
                # The target issued no counter action, and targetted actions
                # cannot be counter actioned by players other than the target.

                return None

            # The target issued a counter action.

            return target

        counterer_player_id = self.next_player(primary_player_id)
        while counterer_player_id == primary_player_id:
            counter_action = self.run_single_counter_action(
                player_id=counterer_player_id,
                primary_action=primary_action,
                primary_player_id=primary_player_id,
            )

            if counter_action != CounterAction.NoCounterAction:
                return counterer_player_id

            counterer_player_id = self.next_player(counterer_player_id)

        return None

    def run_single_counter_action(
        self,
        player_id: int,
        primary_action: PrimaryAction,
        primary_player_id: int
    ) -> CounterAction:
        """
        Returns the counter action issued by the given player.
        """

        player = self.players[player_id]
        game_info = GameInfo(
            requested_move=RequestedMove.CounterAction,
            player_id=player_id,
            balances=self.balances,
            own_cards=player.hand,
            revealed_cards=self.revealed_cards,
            players_cards_num=self.players_cards_num,
            history=self.history,
            current_primary_player_id=primary_player_id,
        )
        player.bot.game_info = game_info

        counter_action = player.bot.counter_action_handler()

        if counter_action == CounterAction.NoCounterAction:
            # The player has issued no CounterAction.
            return CounterAction.NoCounterAction

        # This player has issued a CounterAction.

        if (
            counter_action
            not in PRIMARY_ACTION_TO_COUNTER_ACTIONS[primary_action]
        ):
            # If the CounterAction is not valid for the primary action, we
            # error.
            raise ValueError(
                f'Player {player_id} issued invalid CounterAction '
                f'{counter_action} against PrimaryAction {primary_action}'
            )

        # Otherwise we update the history and return their counter action.

        action = Action(
            action_type=ActionType.CounterAction,
            action=counter_action,
            player_id=player_id,
            successful=None
        )
        self.history[-1][ActionType.CounterAction] = action

        return counter_action

    def resolve_successful_primary_action(
        self,
        primary_player_id: int,
        primary_action: PrimaryAction,
        target: Optional[int]
    ) -> None:
        primary_player = self.players[primary_player_id]

        if primary_action == PrimaryAction.Income:
            primary_player.balance += 1

        elif primary_action == PrimaryAction.ForeignAid:
            primary_player.balance += 2

        elif primary_action == PrimaryAction.Coup:
            if target is None:
                raise ValueError(f'Coup requires a target.')

            self.run_influence_loss(
                player_id=target,
                primary_player_id=primary_player_id
            )

        elif primary_action == PrimaryAction.Tax:
            primary_player.balance += 3

        elif primary_action == PrimaryAction.Assassinate:
            if target is None:
                raise ValueError(f'Assassinate requires a target.')

            self.run_influence_loss(
                player_id=target,
                primary_player_id=primary_player_id
            )

        elif primary_action == PrimaryAction.Exchange:
            primary_player.hand.append(self.draw_card())
            primary_player.hand.append(self.draw_card())
            self.run_discard_to_deck(
                player_id=primary_player_id,
                primary_player_id=primary_player_id
            )
            self.run_discard_to_deck(
                player_id=primary_player_id,
                primary_player_id=primary_player_id
            )

        elif primary_action == PrimaryAction.Steal:
            if target is None:
                raise ValueError(f'Steal requires a target.')

            if self.players[target].balance == 0:
                raise Exception(f'Target for Steal must not have 0 balance.')

            steal_amount = min(self.players[target].balance, 2)
            self.players[target].balance -= steal_amount
            primary_player.balance += steal_amount

        else:
            raise ValueError(f'Unknown PrimaryAction {primary_action}')


    @property
    def remaining_players(self) -> list[Player]:
        """ The players which are not yet eliminated """
        return [p for p in self.players if not p.eliminated]

    @property
    def tied(self) -> bool:
        """ Returns whether completed game was a tie """
        if not self.complete:
            raise Exception("Game is not complete yet!")
        return len(self.remaining_players) > 1

    @property
    def winner(self) -> Player:
        if not self.complete:
            raise Exception("Game is not complete yet!")
        if self.tied:
            raise Exception("Game was a tie")
        return self.remaining_players[0]
