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
import teams
import general
#import roles

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
    await bot.process_commands(msg)

@bot.event
async def on_message_delete(msg):
    e = discord.Embed(title="Deleted Message", description=msg.author.mention, colour=discord.Colour.blue())
    e.add_field(name="Sent at %s" % msg.created_at, value=msg.content)
    await bot.guild.get_channel(bot.MESSAGE_LOG_CHANNEL).send(embed=e)

@bot.event
async def on_reaction_add(reaction, user):
    if user.id != bot.appinfo.id:
        if reaction.message.author.id == bot.appinfo.id:
            await teams.process_invite(reaction, user)
            await teams.process_roster_edit(reaction, user)
            await general.process_get_roles(reaction, user)
        #if reaction.message.channel.id == x:
            #await roles.process_roles(reaction, user)

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

        database.cur.execute("SELECT team FROM playertable WHERE discordid=%s;" % member.id)
        team = database.cur.fetchone()[0]
        if team != None:
            database.cur.execute("SELECT teamroleid FROM teamtable WHERE teamname='%s';" % team)
            troleid = database.cur.fetchone()[0]
            teamrole = bot.guild.get_role(troleid)
            if teamrole == None:
                teamrole = await bot.guild.create_role(name=team, colour=discord.Colour.orange(), hoist=True, mentionable=True)
                await teamrole.edit(permissions=bot.guild.get_role(bot.MEMBER_ROLE).permissions)
                utils.escape_string(team)
                database.cur.execute("UPDATE teamtable SET teamroleid=%s WHERE teamname='%s';" % (teamrole.id, team))
                database.conn.commit()
                await teams.update_role_position(teamname)
            await member.remove_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
            await member.add_roles(teamrole)


@bot.event
async def on_member_remove(member):
    if database.user_registered(member.id):
        await log("%s has left the server." % database.username(member.id))
