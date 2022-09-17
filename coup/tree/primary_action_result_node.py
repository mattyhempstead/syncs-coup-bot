from coup.tree.game_tree_node import NonPrimaryNode, UsuallyStochasticNode

"""END LOCAL IMPORTS"""

from dataclasses import dataclass


@dataclass(kw_only=True)
class PrimaryActionResultNode(NonPrimaryNode, UsuallyStochasticNode):
    def generate_children(
        self, *,
        to_depth: int,
        current_depth: int = 0
    ) -> None:
        """
        Something like this... this was written for a different piece of code
        that no longer exists, so, obviously needs a lot of fixing.
        """

        players = [*self.players]
        perspective_hand = [*self.perspective_hand]

        match self.unresolved_primary_action:
            case PrimaryAction.Income:
                players[self.primary_player_id] = Player(
                    self.primary_player_id,
                    self.players[self.primary_player_id].balance + 1,
                    self.players[self.primary_player_id].card_num,
                    False
                )

            case PrimaryAction.ForeignAid:
                players[self.primary_player_id] = Player(
                    self.primary_player_id,
                    self.players[self.primary_player_id].balance + 1,
                    self.players[self.primary_player_id].card_num,
                    False
                )

            case PrimaryAction.Coup:
                if (
                    self.unresolved_primary_action_target is None
                    or self.unresolved_primary_action_revealed_card is None
                ):
                    raise Exception(
                        'For a Coup action, the target and revealed card must '
                        'be set'
                    )
                
                players[self.unresolved_primary_action_target] = Player(

                )
                
                

            case PrimaryAction.Tax:
                pass

            case PrimaryAction.Assassinate:
                pass

            case PrimaryAction.Exchange:
                pass

            case PrimaryAction.Steal:
                pass

            case other:
                raise ValueError(
                    'Unknown unresolved primary action '
                    f'{self.unresolved_primary_action}'
                )

        next_primary_player = self.next_player_id(self.primary_player_id)

        return PrimaryActionNode(
            players=players,
            revealed_cards=self.revealed_cards,
            primary_player_id=next_primary_player,
            deciding_player_id=next_primary_player,
            perspective_player_id=self.perspective_player_id,
            perspective_hand=perspective_hand
        )
