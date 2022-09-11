
# A list of bot files in a dependency topological order
BOT_FILE_NAMES = [
    'base_bot.py',
    'other_bot.py'
]

FILE_NAMES = [
    'coup/bots/enums.py',
    'coup/bots/action.py',
    'coup/bots/game_info.py',
    'coup/bots/bot_battle.py',
    *(['coup/bots/bots/'+b for b in BOT_FILE_NAMES]),
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
