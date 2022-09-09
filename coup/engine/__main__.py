import ..bots.


def main() -> None:
    bot_battles = [...]
    bots = [some_bot(bot_battles[0])]

    for i in range(turns):
        bots[i % 5].game_info = ...
        bots[i % 5].take_turn()


if __name__ == "__main__":
    main()
