FILE_NAMES = [
    'base_bot/action.py',
    'base_bot/enums.py',
    'base_bot/game_info.py',
    'base_bot/bot_battle.py',
    'base_bot/base_bot.py',
]
OUTPUT = 'submission.py'
DELIMITER = '"""END LOCAL IMPORTS"""'


output = ''
for file_name in FILE_NAMES:
    with open(file_name) as input_file:
        output += input_file.read().split(DELIMITER)[-1]
        output += '\n\n\n\n\n\n\n'


with open(OUTPUT, 'w') as output_file:
    output_file.write(output)
