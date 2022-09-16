# Tree

Code for generating a game tree.

The tree is inherently from the perspective of a single player. The details of the other players are assumed to be unknown.

When objects with identical values are shared between nodes, where possible, they should be identical objects to minimise memory usage.

However, whenever any property changes they must always be completely copied, to avoid accidental mutation of the state of a parent node.

Cards are (permanently) revealed when influence is lost:
- On a challenge success (the person who was challenged lost a card)
- On a challenge failure (the person who made the challenge lost a card)
- On a successful relevant primary action (coup or assassinate)

- **PrimaryActionNode** (child for each (primary action, target) pair - `4 + (3 * 5) = 19`)
  - ChallengeNode (child for each player other than the primary player, and for no player - `5`)
    - (Player challenged) ChallengeResultNode (child for success and failure of challenge - `2`)
      - (Success) RevealedCardNode (challenged primary player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
        - **PrimaryActionNode** (primary action challenge succeeded, primary action failed; **repeats**)
      - (Failure) RevealedCardNode (challenging player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
        - CounterActionPlayerNode (child for each player other than the primary player, and for no player - `5`)
          - (Player countered) CounterActionChoiceNode (child for each possible counter action - `2`)
            - ChallengeNode (child for each player other than the countering player, and for no player - `5`)
              - (Player challenged) ChallengeResultNode (child for success and failure of challenge - `2`)
                - (Success) RevealedCardNode (challenged countering player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
                  - RevealedCardNode (target player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
                    - **PrimaryActionNode** (counter action challenge succeeded, counter action failed, primary action succeeded; **repeats**)
                - (Failure) RevealedCardNode (challenging player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
                  - **PrimaryActionNode** (counter action challenge failed, counter action succeeded, primary action failed; **repeats**)
              - (No player challenged) **PrimaryActionNode** (no counter action challenge, counter action succeeded, primary action failed; **repeats**)
          - (No player countered) - RevealedCardNode (target player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
            - **PrimaryActionNode** (no counter action, primary action challenge failed, primary action succeeded; **repeats**)
    - (No player challenged) CounterActionPlayerNode (child for each player other than the primary player, and for no player - `5`)
      - (Player countered) CounterActionChoiceNode (child for each possible counter action - `2`)
        - ChallengeNode (child for each player other than the countering player, and for no player - `5`)
          - (Player challenged) ChallengeResultNode (child for success and failure of challenge - `2`)
            - (Success) RevealedCardNode (challenged countering player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
              - RevealedCardNode (target player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
                **PrimaryActionNode** (counter action challenge succeeded, counter action failed, primary action succeeded; **repeats**)
            - (Failure) RevealedCardNode (challenging player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
              - **PrimaryActionNode** (counter action challenge failed, counter action succeeded, primary action failed; **repeats**)
          - (No player challenged) **PrimaryActionNode** (no counter action challenge, counter action succeeded, primary action failed; **repeats**)
      - (No player countered) RevealedCardNode (target player lost a card - child for each possible revealed card, or just one child if no card was revealed - `5`)
        **PrimaryActionNode** (no counter action, primary action challenge failed, primary action succeeded; **repeats**)

At largest, for one turn, this is `19 * 5 * 2 * 5 * 5 * 2 * 5 * 2 * 5 * 5 = 2375000`

If at any point the game ends, we have a GameEndNode.