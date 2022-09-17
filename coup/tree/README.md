# Tree

Code for generating a game tree.

The tree is inherently from the perspective of a single player. The details of the other players are assumed to be unknown.

When objects with identical values are shared between nodes, where possible, they should be identical objects to minimise memory usage.

However, whenever any property changes they must always be completely copied, to avoid accidental mutation of the state of a parent node.

The evaluation of a state is designed to be a list of floating point numbers between 0 and 1, one for each player, in the same order as the players. The higher the number, the better it is for that player.

Cards are (permanently) revealed when influence is lost:
- On a challenge success (the person who was challenged lost a card)
- On a challenge failure (the person who made the challenge lost a card)
- On a successful relevant primary action (coup or assassinate)

`make_next_turn_node` is responsible for handling any card loss that results from a primary action. Other card loss should be handled when it occurs.

Card revealing:
- The only times a card is permanently revealed is at a challenge (success or failure) or when a primary action resolves.
- A ChallengeResultNode has one child for card that could possibly be revealed.
  - They are evaluated stochastically if it is not the perspective player deciding.
  - They are evaluated normally if it is the perspective player deciding.
- Before a successful primary action there is a PrimaryActionResultNode.
  - For most primary actions this does nothing other than apply the effects of the primary action, and just has a direct child of a primary action node.
  - For primary actions in which a card is lost, this has one child for each card that could be lost.
    - Same stochastic / decider split depending on whether or not it is the perspective player.

- **PrimaryActionNode** (child for each (primary action, target) pair - `4 + (3 * 5) = 19`)
  - ChallengeNode (child for each player other than the primary player, and for no player - `5`)
    - (Player challenged) ChallengeResultNode (child for each card that could be revealed by whoever looses one - `2 * 5 = 10`)
      - (Success) **PrimaryActionNode** (primary action challenge succeeded, primary action failed; **repeats**)
      - (Failure) CounterActionPlayerNode (child for each player other than the primary player, and for no player - `5`)
        - (Player countered) CounterActionChoiceNode (child for each possible counter action - `2`)
          - ChallengeNode (child for each player other than the countering player, and for no player - `5`)
            - (Player challenged) ChallengeResultNode (child for each card that could be revealed by whoever looses one - `2 * 5 = 10`)
              - (Success) PrimaryActionResultNode (one child for each possible primary action result, most on card reveal - `5`)
                  - **PrimaryActionNode** (counter action challenge succeeded, counter action failed, primary action succeeded; **repeats**)
              - (Failure) **PrimaryActionNode** (counter action challenge failed, counter action succeeded, primary action failed; **repeats**)
            - (No player challenged) **PrimaryActionNode** (no counter action challenge, counter action succeeded, primary action failed; **repeats**)
        - (No player countered) - PrimaryActionResultNode (one child for each possible primary action result, most on card reveal - `5`)
          - **PrimaryActionNode** (no counter action, primary action challenge failed, primary action succeeded; **repeats**)
    - (No player challenged) CounterActionPlayerNode (child for each player other than the primary player, and for no player - `5`)
      - (Player countered) CounterActionChoiceNode (child for each possible counter action - `2`)
        - ChallengeNode (child for each player other than the countering player, and for no player - `5`)
          - (Player challenged) ChallengeResultNode (child for each card that could be revealed by whoever looses one - `2 * 5 = 10`)
            - (Success) PrimaryActionResultNode (one child for each possible primary action result, most on card reveal - `5`)
                **PrimaryActionNode** (counter action challenge succeeded, counter action failed, primary action succeeded; **repeats**)
            - (Failure) **PrimaryActionNode** (counter action challenge failed, counter action succeeded, primary action failed; **repeats**)
          - (No player challenged) **PrimaryActionNode** (no counter action challenge, counter action succeeded, primary action failed; **repeats**)
      - (No player countered) PrimaryActionResultNode (one child for each possible primary action result, most on card reveal - `5`)
        **PrimaryActionNode** (no counter action, primary action challenge failed, primary action succeeded; **repeats**)

At largest, for one turn, this is `19 * 5 * 5 * 5 * 2 * 5 *5 * 5 = 593750`

If at any point the game ends, we have a GameEndNode.

## TODO

- Add pruning.
- Don't expand beyond nodes where we loose
