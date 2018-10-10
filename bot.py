#import thread
import threading
import time
import discord
from discord.ext import commands
import discord
import os
import psycopg2
import math
import asyncio

bot = commands.Bot(command_prefix='!')

CGL_server = 495761319639646208
lobby_category = 497054873678774288

import matchmaking

task = None

@bot.event
async def on_ready() :
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    task = asyncio.create_task(mathmaking.mm_thread())

@bot.event
async def on_message(msg):
    await matchmaking.process_match_commands(msg)
    await bot.process_commands(msg)

#MM_CHANNEL_ID = os.environ['MM_CHANNEL_ID']
MM_CHANNEL_ID = 498928703091507220

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel != None:
        if after.channel.id == MM_CHANNEL_ID and after.channel != before.channel:
            print("join queue")
            matchmaking.mmqueue.push(member.id)
            await member.edit(deafen=True)
    if before.channel != None:
        if before.channel.id == MM_CHANNEL_ID and before.channel != after.channel:
            print("leave queue")
            matchmaking.mmqueue.pop(member.id)
            await member.edit(deafen=False)
