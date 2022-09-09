from coup.bots.enums import Character
from coup.bots.base_bot import BaseBot


class Player:
    def __init__(self, bot: BaseBot, hand: list[Character]):
        self.bot = bot
        self.hand = hand

        self.eliminated = False
        self.balance = 2
