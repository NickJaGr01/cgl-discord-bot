import bot
import os
from discord.ext import commands

import matchmaking
import general_cog
import owner_cog
import mod_cog
import mm_cog
import teams_cog
import stats_cog

token = os.environ['DISCORD_KEY']
bot.bot.run(token)
