from coup.bots.enums import Character, PrimaryAction, CounterAction

"""END LOCAL IMPORTS"""


NUMBER_OF_PLAYERS = 5
NUMBER_OF_EACH_CARD_IN_DECK = 3
SIZE_OF_DECK = NUMBER_OF_EACH_CARD_IN_DECK * len(Character)


PRIMARY_ACTION_TO_CARD: dict[PrimaryAction, Character] = {
    PrimaryAction.Tax: Character.Duke,
    PrimaryAction.Assassinate: Character.Assassin,
    PrimaryAction.Exchange: Character.Ambassador,
    PrimaryAction.Steal: Character.Captain,
}


COUNTER_ACTION_TO_CARD: dict[CounterAction, Character] = {
    CounterAction.BlockForeignAid: Character.Duke,
    CounterAction.BlockStealingAsCaptain: Character.Captain,
    CounterAction.BlockStealingAsAmbassador: Character.Ambassador,
    CounterAction.BlockAssassination: Character.Contessa,
}


PRIMARY_ACTION_TO_COST: dict[PrimaryAction, int] = {
    PrimaryAction.Income: 0,
    PrimaryAction.ForeignAid: 0,
    PrimaryAction.Coup: 7,
    PrimaryAction.Tax: 0,
    PrimaryAction.Assassinate: 3,
    PrimaryAction.Exchange: 0,
    PrimaryAction.Steal: 0,
}


PRIMARY_ACTION_TO_COUNTER_ACTIONS: dict[PrimaryAction, set[CounterAction]] = {
    PrimaryAction.Income: set(),
    PrimaryAction.ForeignAid: {CounterAction.BlockForeignAid},
    PrimaryAction.Coup: set(),
    PrimaryAction.Tax: set(),
    PrimaryAction.Assassinate: {CounterAction.BlockAssassination},
    PrimaryAction.Exchange: set(),
    PrimaryAction.Steal: {
        CounterAction.BlockStealingAsAmbassador,
        CounterAction.BlockStealingAsCaptain
    },
}


PRIMARY_ACTION_HAS_TARGET: dict[PrimaryAction, bool] = {
    PrimaryAction.Income: False,
    PrimaryAction.ForeignAid: False,
    PrimaryAction.Coup: True,
    PrimaryAction.Tax: False,
    PrimaryAction.Assassinate: True,
    PrimaryAction.Exchange: False,
    PrimaryAction.Steal: True,
}
