from coup.bots.enums import Character
from coup.bots.bots.base_bot import BaseBot


class Player:
    def __init__(self, bot: BaseBot, player_id: int, hand: list[Character]):
        self.bot = bot
        self.player_id = player_id
        self.hand = hand

        self.balance = 2

    @property
    def eliminated(self) -> bool:
        return len(self.hand) == 0

    def __repr__(self):
        return f'P{self.player_id} ({str(self.bot)})'
