import bot
import os
from discord.ext import commands

import matchmaking
import cgl_commands

token = os.environ['DISCORD_KEY']
bot.bot.run(token)
