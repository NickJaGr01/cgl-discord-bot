import bot
import os
from discord.ext import commands

bot.bot = commands.Bot(command_prefix='!')
bot.MM_CHANNEL_ID = os.environ['MM_CHANNEL_ID']

import matchmaking
import cgl_commands

token = os.environ['DISCORD_KEY']
bot.bot.run(token)
