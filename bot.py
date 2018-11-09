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
from utils import *

bot = commands.Bot(command_prefix='!')

import teams

async def background_thread():
    bot.delta_time = 0
    loop = asyncio.get_event_loop()
    last_time = loop.time()
    while True:
        now = loop.time()
        bot.delta_time = now - last_time
        last_time = now

        await asyncio.sleep(.1)

@bot.event
async def on_ready() :
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
    bot.CAPTAIN_ROLE = int(os.environ['CAPTAIN_ROLE'])
    bot.PLAYER_ROLE_ROLES = {
        "awper": int(os.environ['AWPER_ROLE']),
        "rifler": int(os.environ['RIFLER_ROLE']),
        "igl": int(os.environ['IGL_ROLE']),
        "entry": int(os.environ['ENTRY_ROLE']),
        "lurker": int(os.environ['LURKER_ROLE']),
        "support": int(os.environ['SUPPORT_ROLE'])
    }
    bot.LOG_CHANNEL = int(os.environ['LOG_CHANNEL'])

    #bot.task = asyncio.create_task(background_thread())

@bot.event
async def on_message(msg):
    await bot.process_commands(msg)

@bot.event
async def on_reaction_add(reaction, user):
    if user.id != bot.appinfo.id:
        if reaction.message.author.id == bot.appinfo.id:
            await teams.process_invite(reaction, user)
            await teams.process_roster_edit(reaction, user)

@bot.event
async def on_member_join(member):
    #check if this user was previously a registered member
    if database.user_registered(member.id):
        username = database.username(member.id)
        await member.edit(nick=username)
        await member.add_roles(bot.guild.get_role(bot.MEMBER_ROLE))
        await member.add_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
        await member.send("Welcome back to CGL! We're glad you came back.")
        await log("%s rejoined the server." % (member.mention))

@bot.event
async def on_member_remove(member):
    if database.user_registered(member.id):
        database.cur.execute("UPDATE playerTable SET team=NULL WHERE discordID=%s;" % member.id)
        #check if the member is the captain of a team
        database.cur.execute("SELECT teamname FROM teamTable WHERE captainID=%s;" % member.id)
        team = database.cur.fetchone()
        await log("%s has left the server." % database.username(member.id))
        if team != None:
            team = team[0]
            await teams.disband_team(team, "Your team has been disbanded because your captain has left the server.")
