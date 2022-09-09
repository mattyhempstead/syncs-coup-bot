FILE_NAMES = [
    'bots/action.py',
    'bots/enums.py',
    'bots/game_info.py',
    'bots/bot_battle.py',
    'bots/base_bot.py',
    'bots/other_bot.py',
    'bots/run.py',
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
