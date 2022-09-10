from coup.bots.enums import Character
from coup.bots.base_bot import BaseBot


class Player:
    def __init__(self, bot: BaseBot, player_id: int, hand: list[Character]):
        self.bot = bot
        self.player_id = player_id
        self.hand = hand

        self.balance = 2

    @property
    def eliminated(self) -> bool:
        return len(self.hand) == 0
