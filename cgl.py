import bot
import os
from discord.ext import commands

import general_cog
import owner_cog
import admin_cog
import teams_cog
import stats_cog

token = os.environ['DISCORD_KEY']
bot.bot.run(token)

import http_server
http_server.start_listening()
