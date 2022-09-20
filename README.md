# Alpha Coup

Some [coup](https://en.wikipedia.org/wiki/Coup_(game)) bot thing or something.

Developed in collaboration with [James](https://github.com/thewrongjames).

For the SIG x SYNCS 2022 Bot Battle competition. Final results can be seen [here](https://public.flourish.studio/visualisation/11216584/) via 1 day average of win rate.

Huge thanks to all the SYNCS execs who spent, as I was told, 100+ hours of coding to get the competition ready.


## Approach

### Bot Strategy

Our final bot (see [here](https://github.com/mattyhempstead/syncs-coup-bot/blob/main/coup/bots/bots/main_bot.py) for a file of mostly comments and some bot) was relatively simple compared to some of the more advanced strategies humans use to play Coup.

Underlying the bot strategy was a (mostly) honest perfect information approach to playing Coup. Some examples of this in our final bot include:
 - Couping whenever feasible (>=7 coins)
 - Performing primary actions when we hold the appropriate cards and the required coins or player requirements.
 - Avoiding primary actions against players who have historically countered them.
 - Using Foreign Aid to gather coins, unless an (alive) player has historically countered it.
 - Countering all actions when we hold the appropriate card.
 - Challenging all actions that were certainly lies as deduced by analysing the current list of publically revealed cards, plus our own private hand. There was some work put in to utilise temporarily-revealed cards (e.g. through Exchanges or successful Challenge counters) that have been returned to the deck, which could would remain "revealed" until another player was seen interacting with the deck. However we ultimately ran out of time to implement this feature, though the effect would have likely been quite minimal.
 - Revealing the appropriate card when challenged ourselves.
 - Fake blocking assassination when a single card remained, as the certain alternative is losing the game.
 - Many more things...
 
Note that for many of the above actions (e.g. honestly blocking or responding to challenges), human players may often perform advanced lying strategies which put themselves at a temporary disadvantage in order to trick their opponents into thinking they lack certain cards. However, these types of strategies were found rarely effective against the particular botted competition.

On top of the above (mostly) honest perfect information player, laid a number of carefully designed decisions that were purely implemented as our experiments revealed them to be the statistically best option in order to maximise our chances of winning.
 - A carefully optimised discard order priority for the various card types. In order of cards we value the most to the least it went: Captain, Duke, Assassin, Ambassador, and Contessa. Interestingly, the importance of the first two cards suggest that the best cards to keep after losing one are those that increase your coins the most relative to other players (stealing 2 coins via Captain is effectively +4, where as Tax via Duke is +3).
 - A carefully optimsed priority of primary actions (e.g. Couping with the highest priority, then Assassinating, then Duke, then Stealing, then other income methods). The Income action had the lowest priority and was almost always a bad idea.
 - When targeting players for a Coup or Assassination, our experiments showed it was usually best to target the player who had the most remaining cards. If that was a tie, the next best order should be based on the number of coins.
 - When targeting players for a Steal, we would avoid anybody with less than 5 coins. Originally we figured that targeting players with 2 or more coins would be optimal as this means you could obtain the maximum benefit of +2 coins from the steal. However, we noticed that setting this limit to 3 resulted in a higher winrate, and the winrate kept increasing as we increased the threshold. After 5 coins the winrate started to decrease, suggesting >=5 coins was the global maximum for Stealing. This may be because, at 5 coins, a opponent is quite likely to reach a state where they can Coup within a single turn as there are many ways to obtain 2 coins in a single turn (e.g. Stealing, Foreign Exchange, Tax). At 4 or less coins, a opponent is much less of a threat and so you may be better off performing selfish actions like Tax.

Other than blocking when being assassinated with a single card to prevent certain death, the above bot was entirely honest. We did, however, implement a number of bluffing strategies much later in the competition as discussed below.


### Meta Strategy

For the vast majority of the competition (~13.9 days of the 2 weeks), our bot was what we called a (mostly) honest bot, and was optimised entirely under that constraint. Rather than spending time developing and testing bluffing techniques against our live opponents, we spent the entire time optimsing aspects of our bot that did not involve lying. As discussed, this meant finding the perfect circumstances to perform primary actions, finding the optimal card discard order, and discovering the best opponents to attack or steal from when we held the appropriate card.

This self-enforced restriction was enirely intentional. The idea was that by leaving our bot honest until the end of the competition, we would discourage the development of any well performing bots that risked calling bluffs in situations where the bluff was not certain. In theory, people who did try making bots that called bluffs would find that they were often punished in winrate, as one of the high performing bots rarely ever lied.

It was then, in the final few hours of the competition, that we performed a complete 180 and started lying more aggressively than any of our competitors had before, and thus more than any of our competitors were expecting. As hoped, nobody had prepared for it any the tendency to call bluffs was very low. We therefore used the remaining time to quickly develop a number of dishonest strategies that had the biggest impact on winrate against our opponents. These included:
 - A highly beneficial bluff that we implemented was always attacking the *previous* player whenever they become a theat. When analysing the game history, we noticed that a very large number of primary action attacks from our opponents (Coup, Assassinate, Steal) were targeting the player whose turn was directly after them. This was because, due to the algorithmic nature of the bots, players were often scanned in turn order when choosing who to attack. Thus, when there were two equally valid targets, the one who was positioned earlier was often attacked first as they would be encountered first by the loop. This was taken to the extreme with the 7 examples bots provided, who would always attack the first alive player in turn order. Therefore, whenever the player before us had at least 7 coins and could Coup, there was a very high likelihood that they would attack us specifically next turn. In this scenario, we found the best option was to use our turn to Steal from them if they had 7 or 8 coins (thus putting them below the 7 coin Coup threshold), or attempt to Assassinate them if they had 9 or more coins as Stealing would not be enough. We would do this regardless of whether or not we had the cards to support it, as the risk of having our Bluff caught was found to be less significant than the high chance of being Couped next turn.
 - Another important bluff was claiming Tax in place of Income, but specifically after turn 16 (unless 3 Dukes had already been revealed). This may seem a little counter-intuive, however the nature of the competition seemed to have it that the few players who over aggressively challenged cards (e.g. the example *Challenger* bot) would be quickly eliminated due to false claims. However, this meant that lying early game was risky as it would place you in the line of attack from these somewhat suicidal bots. For this reason, we waited for a few rounds of plays before starting to bluff on more minor actions like obtaining coins. This is quite different from real life games against humans, where players will often lie more aggressively near the start of the game (often claiming Duke), as the game information is low and so the uncertainty/risk in challenging remains high.
 - The last decision which may seem silly but experiments revealed to be statistically beneficial, was to simply block every single Assassination or Steal attempt at all times, regardless of which cards have been revealed or any other game history. This decision was simply a concequence of the other bots that happen to exist which, on average, made the net risk of having your bluff challenged lower than the net benefit you get from never succumbing to these attacks. A contributing factor for this may have been the negative reinforcement against challenges that our honest bot had pushed for the majority of the competition.


### Meta Meta Strategy

Although the above strategy of negatively reinforcing bluff calling bots was effective, there was an even more important approach we took that helped us develop a effective bot.

In fact, before developing even a basic honest bot, we spent a couple days completely rewriting the python Coup engine from scratch locally (see `coup/engine`). This was a crutial step, as it allowed us to develop and test our bots at a much more rapid pace than what is possible from manually uploading each iteration of the bot to the leaderboard and waiting nearly a minute to see the results from a single game.

Having a local engine allowed us to detect errors almost instantaneously. After any changes, we could just simulate 1000 random games in a few seconds which would usually provide 100% code coverage to check for any possible Exceptions. We could also debug and step through specific game situations locally to see why our bot was misbehaving on the leaderboard. I'll admit, at one point we were actually last place on the leaderboard thanks to our 4D chess strategy of self-assassination, which the local simulator thankfully helped debug.


### Meta Meta Meta Strategy

Lastly, as the cherry on top, we developed one final layer of abstraction of what was essentially a wrapper over the engine to simulate realistic leaderboard competition (see `coup/analysis`).

We started by asking a number of suspicious questions to the SYNCS exec team, querying about the exact method for which the final leaderboard rankings would be determined. From the responses, we gathered that the final rankings would use winrate % as the metric (as oppose to ELO, which the leaderboard was currently utilising).
This was incredibly important, as it meant we could theoretically develop a wrapper to our engine that would play tens of thousands of games against other bots we develop, and have it spit out a winrate % that we can optimise directly against. And so that was exactly what we did, thus allowing us to not only rapidly test our bots, but also rapidly improve our bots by just hill climbing strategies locally to maximise winrate against other bots we develop.

However, for this type of local hill climbing approach, one needs to be careful as to not overfit to the simulated competition. Optimising bot A against a bot B, might at one point actually reduce performance against another bot C. For this reason, we set out to gather more information about the exact makeup of the competition in the leaderboard. One crutial piece of information was that the [7 example bots](https://github.com/syncs-usyd/coup-example-submissions) would be included in games which calculate winrate %. Knowing this, we of course decided to recreate 1:1 copies of all 7 examples bots in our local simulator. As there were 14 other teams competing, we also developed 14 other "reasonable" bots (using past versions of our own bot). These 21 bots were then placed in bot pool, of which we randomly sampled 4 bots per game to compete with our fifth to simulate as realistic a scenario as possible, and thus as close an approximation of the true winrate % as we could.

This final bot pool was quite important for various reasons. For one, there were a number of bots that had quite extreme strategies (e.g. always challenging or always countering). Although these bots rarely won games, their participation did have a large affect on the performance of other higher quality bots. For example, having a bot that challenged all turns meant there was a much higher proability of having bluffs challenged, at least in the early game until that challenger bot was eliminated. Therefore, by including this example bot in our local simulations, we were able to hill climb strategies that took into account the existance of bots like these, and optimise accordingly.


### Outcome

If it isn't clear by now, we may have gone a little overboard with our strategy. The final results can be seen [here](https://public.flourish.studio/visualisation/11216584/) which shows a 1 day average of win rate over the course of the competition for each bot. Notice how our bot (Alpha Coup) once introduced, remains relatively stable near the top of the competition as we optimise our honest bot using the local simulator. Then, in the final couple hours of the competition we upload the bot that starts lying aggressively. The final day shown in the visualation did not allow any more code uploads, and you can see the 1-day average winrate of our bot skyrocket as nobody else had prepared for that type of strategy.

Overall, this competition was a lot of fun and we really appreciate the effort from the SYNCS+SIG that made it possible. In retrospect, we both probably should have spent more time on our uni assignments and less on the strategy overkill, but it was interesting to see just how high a winrate we could achieve. Winning ~70% of games against 4 others players is quite a bit excessive.


## Codebase

This codebase is a mess, but, well, we didn't have a lot of time to work on it. It's all in a top level folder called `coup` so we could use python module stuff, because python imports are a dark art.

To run our simulator / analysis stuff, run `python -m coup.analysis` from the top level of the repo. This will spit out a bunch of pandas/numpy tables that give insight of the performance of our final bot (`main_bot.py`).

`coup/bots` very helpfully contains another folder called `bots` which contains our bots. Obviously. They inherit from `coup.bots.bots.base_bot` so that they can be run by the engine.

Speaking of which, the engine is in `coup/engine` it is largely a single huge mess of a file.  It almost certainly has logic errors, but, well, it runs.

There's also `coup/tree`, which was a very failed attempt to make a tree search for the game. Several files were left "in progress" when I abandoned it.

The rest of this readme is just what we were writing whilst we were working.

## TODidn't:

- Move common stuff into common (and ensure make submission still works).
- Fix type errors.
- Enforce keyword arguments to methods in engine.

