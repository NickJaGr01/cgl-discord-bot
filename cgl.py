import bot
import os

bot.bot = commands.Bot(command_prefix='!')
bot.MM_CHANNEL_ID = os.environ['MM_CHANNEL_ID']

token = os.environ['DISCORD_KEY']
bot.bot.run(token)
