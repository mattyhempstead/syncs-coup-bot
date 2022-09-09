FILE_NAMES = [
    'coup/bots/enums.py',
    'coup/bots/action.py',
    'coup/bots/game_info.py',
    'coup/bots/bot_battle.py',
    'coup/bots/base_bot.py',
    'coup/bots/other_bot.py',
    'coup/bots/run.py',
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
