from enum import IntEnum


class Character(IntEnum):
    Duke = 1
    Assassin = 2
    Ambassador = 3
    Captain = 4
    Contessa = 5

    def __repr__(self) -> str:
        return f"<C_{self.name}>"


class ActionType(IntEnum):
    PrimaryAction = 1
    ChallengePrimaryAction = 2
    CounterAction = 3
    ChallengeCounterAction = 4


class PrimaryAction(IntEnum):
    Income = 1
    ForeignAid = 2
    Coup = 3
    Tax = 4
    Assassinate = 5
    Exchange = 6
    Steal = 7


class ChallengeAction(IntEnum):
    NoChallenge = 0
    Challenge = 1


class CounterAction(IntEnum):
    NoCounterAction = 0
    BlockForeignAid = 1
    BlockStealingAsCaptain = 2
    BlockStealingAsAmbassador = 3
    BlockAssassination = 4


ActionEnum = PrimaryAction | CounterAction | ChallengeAction


class RequestedMove(IntEnum):
    PrimaryAction = 1
    ChallengeAction = 2
    ChallengeResponse = 3
    CounterAction = 4
    DiscardChoice = 5
