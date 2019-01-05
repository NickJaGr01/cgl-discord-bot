import bot
import os
from discord.ext import commands

import general_cog
import owner_cog
import admin_cog
import teams_cog
import stats_cog

import http
http.start_listening()

token = os.environ['DISCORD_KEY']
bot.bot.run(token)
