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
from bot import bot

@bot.event
async def on_message(msg):
    if msg.channel.id == bot.ANNOUNCEMENTS_CHANNEL:
        database.cur.execute("SELECT string FROM settings WHERE key='sponsor_ad';")
        ad = database.cur.fetchone()[0]
        if len(ad) > 0:
            database.cur.execute("SELECT int FROM settings WHERE key='last_ad_id';")
            lastad = database.cur.fetchone()[0]
            if lastad != None:
                announcements = bot.guild.get_channel(bot.ANNOUNCEMENTS_CHANNEL)
                await announcements.get_message(lastad).delete()
                newmsg = await announcements.send(ad)
                database.cur.execute("UPDATE settings SET int=%s WHERE key='last_sponsor_id';" % newmsg.id)

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
