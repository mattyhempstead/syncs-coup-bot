# Alpha Coup

Some coup bot thing or something.

## TODO:

- Move common stuff into common (and ensure make submission still works).
- Fix type errors.
- Enforce keyword arguments to methods in engine.

## Engine

Run with `python -m coup.engine`.

## Maths


`1 - 12/15 * 11/14 = 0.37`
So ~37% chance of having a given Character.
i.e. Around 1/3 games we can block assassinations.


`9/15 * 8/14 = ~0.34`
So ~34% chance of not having two given characters.
e.g. 1/3 chance of not having Duke OR Captain



## End Games

### 1. 
 - Two players (including us) remain with 1 card each
 - Opponent has >=7 coins and so will certainly coup next turn
 - We should certainly do one of the possible actions to stop them from couping, since we lose otherwise.
 - Coup (this is forced if we have 7 coins or more)
     - This could be pointless if opponent has 2 cards
     - We should try to avoid self-forced coup's if we expect to be in this situation next turn
 - Assassinate (or fake assassinate) if we have enough coins
 - Steal (or fake steal) this will make the opponent drop below 7 coins

### 2.
- We have a single card left
- Some opponent has just primaried an assassination on us
- We should certainly stop the assassination through any means possible
- Block with Contessa if we have it (or fake block)
- Challenge their Assassin (this probably less optimal against honest players)


### 3.
 - A single opponent remains with one card left
 - We have Assassin card
 - We should probably assassinate as our highest priority move
    - Opponent might block
      - We could perhaps check if they historically have blocked assassinations or historically been honest?
      - If not, they are probably lying and we can challenge it.
      - Just gotta be careful here risk wise.


