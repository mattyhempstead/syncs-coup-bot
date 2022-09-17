from coup.bots.enums import *
from coup.bots.bots.base_bot import BaseBot

"""END LOCAL IMPORTS"""

from typing import Optional
import random


class MainBot(BaseBot):
    """
        Our main submission bot.
    """
    def primary_action_handler(self) -> tuple[PrimaryAction, Optional[int]]:

        # We must coup if we can afford it (technically if >=10)
        if self.game_info.current_player.balance >= 7:
            # TODO: Find who to coup

            # Likely a good idea is to coup the player who seems to be "best"
            # This might be in cards or coins, but could also be one with the best history of killings
            # Especially in late game, if a player has eliminated many they will probably eliminate more.

            # In a sim I ran, if everyone is couping the winning player, then the player who coups
            # the richest has an advantage. Alternatively, if everyone is couping the richest, then
            # the player who coups the winning has an advantange. Interesting that this happens.

            # Coup if another player will coup next turn            
            # This doesn't seem to improve
            # richest_player = self.game_info.get_richest_player()
            # if richest_player.balance >= 7:
            #     return (PrimaryAction.Coup, richest_player.player_id)


            if random.random() < 0.5:
                target_player = self.game_info.get_winning_player()
            else:
                target_player = self.game_info.get_richest_player()


            # target_player = self.game_info.get_richest_player()
            # target_player = self.game_info.get_winning_player()
            return (PrimaryAction.Coup, target_player.player_id)


        # if Character.Ambassador in self.game_info.own_cards and self.game_info.turn < 4:
        #     return (PrimaryAction.Exchange, None)


        # if self.game_info.current_player.balance == 6 and Character.Duke not in self.game_info.own_cards:
        #     return (PrimaryAction.Income, None)

        # Prioritize Duke over Assassination if it puts us in a position to COUP
        # if Character.Duke in self.game_info.own_cards and self.game_info.current_player.balance >= 4:
        #     return (PrimaryAction.Tax, None)


        # if self.game_info.current_player.balance >= 3:
        if Character.Assassin in self.game_info.own_cards and self.game_info.current_player.balance >= 3:
            # Avoiding players who historically block is important, obviously
            # Idk whether to start applying this stuff now or waiting until the deadline approaches
            target_player = self.game_info.get_winning_player_without_counter(CounterAction.BlockAssassination)
            if target_player is not None:
                return (PrimaryAction.Assassinate, target_player.player_id)

        if Character.Duke in self.game_info.own_cards:
            return (PrimaryAction.Tax, None)

        if Character.Captain in self.game_info.own_cards:

            # target_player = self.game_info.get_winning_player_without_counter(CounterAction.BlockStealingAsCaptain)
            # if target_player is not None and target_player.balance >= 5:
            #     return (PrimaryAction.Steal, target_player.player_id)

            richest_player = self.game_info.get_richest_player()  # >=5 is best?

            # Steal if we can get 2 coins
            if richest_player.balance >= 5:
                return (PrimaryAction.Steal, richest_player.player_id)


            # Maybe steal from people with >=3 who have successfully assassinated a player in the past
            # if richest_player.balance >= 4 and 

            # Steal if it gives us a coup opportunity
            # if richest_player.balance == 1 and self.game_info.current_player.balance == 6:
            #     return (PrimaryAction.Steal, richest_player.player_id)








        # This will very likely be better assuming the opponent does not challenge
        # We should hold this off until closer to the deadline
        # Pretending to have Duke is a very good and safe strategy!
        # if self.game_info.current_player.balance == 4:
        #     return (PrimaryAction.Tax, None)


        # if self.game_info.turn == 0:
        #     return (PrimaryAction.Tax, None)
        # if self.game_info.turn < 4:
        #     return (PrimaryAction.Tax, None)
        # return (PrimaryAction.Tax, None)


        # Get $2 from Foreign Aid if nobody alive has historically countered it
        if not self.game_info.exists_historical_counter(CounterAction.BlockForeignAid, alive=True):
            return (PrimaryAction.ForeignAid, None)

        # If all else fails get $1 from Income by default
        return (PrimaryAction.Income, None)



    def counter_action_handler(self) -> CounterAction:
        action = self.game_info.get_history_primary_action()


        # if action.action == PrimaryAction.Assassinate:
            # return CounterAction.BlockAssassination

        # Pretending to block            
        # if action.action == PrimaryAction.ForeignAid:
        #     return CounterAction.BlockForeignAid

        # Block foreign aid if we can
        if Character.Duke in self.game_info.own_cards:
            if action.action == PrimaryAction.ForeignAid:
                return CounterAction.BlockForeignAid

        # Block assassination if we can
        if Character.Contessa in self.game_info.own_cards:
            if action.action == PrimaryAction.Assassinate:
                return CounterAction.BlockAssassination

        # Block stealing if we can (as Captain)
        if Character.Captain in self.game_info.own_cards:
            if action.action == PrimaryAction.Steal:
                return CounterAction.BlockStealingAsCaptain

        # Block stealing if we can (as Ambassador)
        if Character.Ambassador in self.game_info.own_cards:
            if action.action == PrimaryAction.Steal:
                return CounterAction.BlockStealingAsAmbassador


        # Fake block assassination with Contessa if we will certainly lose otherwise
        if self.game_info.current_player.card_num == 1 and action.action == PrimaryAction.Assassinate:
            return CounterAction.BlockAssassination


        return CounterAction.NoCounterAction


    def challenge_action_handler(self) -> ChallengeAction:
        """
        TODO: Conservative check we should challenge if not challenging results in certain loss
        TODO: Conservative check we should challenge when logically impossible (e.g. revealed cards + our cards == 3 of char)

        TODO: Likely scenarios of faking
          - A player avoids countering when possible (e.g. on a foreign aid), then claims the benefit from that card (e.g. tax)
          - A player calls Contessa when they have one card left (since they will lose unless they counter)
          - A player performs 3 different Actions (meaning they dont have at least one of them)
        """
        if self.game_info.is_lying():
            return ChallengeAction.Challenge

        return ChallengeAction.NoChallenge


    def challenge_response_handler(self) -> int:
        """
            Which card number we reveal if we are challenged (for a primary or a counter).

            If we are honest, we usually want to reveal the correct card unless we are mega-braining.
        """
        if ActionType.CounterAction in self.game_info.history[-1]:
            action = self.game_info.get_history_counter_action()

            # Reveal Duke if we are challenged for blocking ForeignAid
            if action.action == CounterAction.BlockForeignAid and Character.Duke in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Duke)

            # Reveal Captain if we are challenged for blocking Steal
            if action.action == CounterAction.BlockStealingAsCaptain and Character.Captain in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Captain)

            # Reveal Ambassador if we are challenged for blocking Steal
            if action.action == CounterAction.BlockStealingAsAmbassador and Character.Ambassador in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Ambassador)

            # Reveal Contessa if we are challenged for blocking Assassination
            if action.action == CounterAction.BlockAssassination and Character.Contessa in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Contessa)

        else:
            action = self.game_info.get_history_primary_action()

            # Reveal Duke if we are challenged for Tax
            if action.action == PrimaryAction.Tax and Character.Duke in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Duke)

            # Reveal Captain if we are challenged for Stealing
            if action.action == PrimaryAction.Steal and Character.Captain in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Captain)

            # Reveal Assassin if we are challenged for Assassinating
            if action.action == PrimaryAction.Assassinate and Character.Assassin in self.game_info.own_cards:
                return self.game_info.get_character_location(Character.Assassin)

        return 0

    def discard_choice_handler(self) -> int:
        """
            Which card to discard if we are assassinated or couped.
        """

        # This could definitely be a nice loop but for now I'm just being explicit 
        # until the strategy abstractions are clearer

        # We have 4 cards at the beginning of an exchange with 2 card
        # if len(self.game_info.own_cards) == 4:
        #     return self.game_info.get_character_location(Character.Ambassador)




        if Character.Contessa in self.game_info.own_cards:
            return self.game_info.get_character_location(Character.Contessa)

        if Character.Assassin in self.game_info.own_cards:
            return self.game_info.get_character_location(Character.Assassin)

        if Character.Duke in self.game_info.own_cards:
            return self.game_info.get_character_location(Character.Duke)

        if Character.Ambassador in self.game_info.own_cards:
            return self.game_info.get_character_location(Character.Ambassador)

        if Character.Captain in self.game_info.own_cards:
            return self.game_info.get_character_location(Character.Captain)
        


        # Initial guess: Duke, Assassin, Captain, Contessa, Ambassador

        # Are assassins are relatively useless in endgame where we always block?
        # Only if opponent also blocks.

        # Mostly looks like stealing (and blocking) near endgame is very important?

        # Self Sim 26.5%: Captain, Ambassador, Duke, Assassin, Contessa
        # Self Sim 24.0%: Captain, Duke, Assassin, Contessa, Ambassador
        # Self Sim 24.0%: Captain, Assassin, Duke, Contessa, Ambassador
        # Self Sim 22.5%: Duke, Captain, Assassin, Contessa, Ambassador


        raise Exception("What else is there to discard??")
