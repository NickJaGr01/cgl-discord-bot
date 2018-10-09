#import thread
import threading
import time
import discord
from discord.ext import commands
import discord
import os
import psycopg2
import math

bot = None

CGL_server = None
lobby_category = None

import matchmaking
import cgl_commands

@bot.event
async def on_ready() :
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    CGL_server = bot.get_guild(os.environ["OFFICIAL_DISCORD_ID"])
    lobby_catergory = bot.get_channel(os.environ["LOBBY_CATEGORY_ID"])

    try:
        threading.Thread(target=matchmaking.mm_thread).start()
    except:
        print('Error: unable to start thread')

@bot.event
async def on_message(msg):
    matchmaking.process_match_commands(msg)
    await bot.process_commands(msg)

MM_CHANNEL_ID = None

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel.id == MM_CHANNEL_ID and before.channel.id != MM_CHANNEL_ID:
        matchmaking.mmqueue.push(member.id)
        await member.edit(deafen=True)
    elif after.channel.id != MM_CHANNEL_ID and before.channel.id == MM_CHANNEL_ID:
        matchmaking.mmqueue.remove(member.id)
        await member.edit(deafen=False)
