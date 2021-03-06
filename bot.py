#import thread
import threading
import time
import discord
from discord.ext import commands
import os
import psycopg2
import math
import asyncio
from datetime import datetime
import database
import requests

bot = commands.Bot(command_prefix='!')

import teams
import matches

async def background_thread():
    bot.delta_time = 0
    loop = asyncio.get_event_loop()
    last_time = loop.time()
    while True:
        now = loop.time()
        bot.delta_time = now - last_time
        last_time = now
        await thread_update()
        await asyncio.sleep(1)

secs = 0
async def thread_update():
    global secs
    await matches.check_matches()
    secs += bot.delta_time
    if secs >= 300:
        r = requests.get('https://cgl-discord-bot.herokuapp.com/')
        print("ping sent")
        secs = 0

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    bot.NOT_REGISTERED_MESSAGE = "Please register before participating in CGL. You can register by using the \"!register *username*\" command."
    bot.appinfo = await bot.application_info()
    bot.CGL_server = int(os.environ['CGL_SERVER'])
    bot.guild = bot.get_guild(bot.CGL_server)
    bot.MEMBER_ROLE = int(os.environ['MEMBER_ROLE'])
    bot.FREE_AGENT_ROLE = int(os.environ['FREE_AGENT_ROLE'])
    bot.REPORTS_CHANNEL = int(os.environ['REPORTS_CHANNEL'])
    bot.NA_ROLE = int(os.environ['NA_ROLE'])
    bot.EU_ROLE = int(os.environ['EU_ROLE'])
    bot.NA_HUB = os.environ['NA_HUB']
    bot.EU_HUB = os.environ['EU_HUB']
    #bot.CAPTAIN_ROLE = int(os.environ['CAPTAIN_ROLE'])
    bot.PLAYER_ROLE_ROLES = {
        "captain": int(os.environ['CAPTAIN_ROLE']),
        "awper": int(os.environ['AWPER_ROLE']),
        "rifler": int(os.environ['RIFLER_ROLE']),
        "igl": int(os.environ['IGL_ROLE']),
        "entry": int(os.environ['ENTRY_ROLE']),
        "lurker": int(os.environ['LURKER_ROLE']),
        "support": int(os.environ['SUPPORT_ROLE'])
    }
    bot.LOG_CHANNEL = int(os.environ['LOG_CHANNEL'])
    bot.ANNOUNCEMENTS_CHANNEL = int(os.environ['ANNOUNCEMENTS_CHANNEL'])
    bot.STANDIN_CHANNEL = int(os.environ['STANDIN_CHANNEL'])
    bot.TEAMS_BOTTOM_END_ROLE = int(os.environ['TEAMS_BOTTOM_END_ROLE'])
    bot.TEAMS_TOP_END_ROLE = int(os.environ['TEAMS_TOP_END_ROLE'])
    bot.MESSAGE_LOG_CHANNEL = int(os.environ['MESSAGE_LOG_CHANNEL'])
    bot.MAX_TEAM_SIZE = 10
    bot.LIST_EMOJIS = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟", "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵"]


    bot.task = asyncio.create_task(background_thread())



import events
