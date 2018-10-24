from discord.ext import commands
import os
import discord
import database
from bot import bot
import json
from cgl_converters import *

PLAYER_STATS_DICT = {
    "maps": {
        "dust2": {"wins": 0, "total": 0},
        "mirage": {"wins": 0, "total": 0},
        "cache": {"wins": 0, "total": 0},
        "inferno": {"wins": 0, "total": 0},
        "nuke": {"wins": 0, "total": 0},
        "overpass": {"wins": 0, "total": 0},
        "inferno": {"wins": 0, "total": 0}
    }
}

class General:
    @commands.command(pass_context=True)
    async def register(self, ctx, username):
        """register as a member in the league
        Before players can participate in league activities, they must register for the league.
        Upon registration, the player's server nickname will be changed to the one given.
        The player will also be given the Member and Free Agent roles."""
        if not database.user_registered(ctx.author.id):
            if username == None:
                await ctx.send("Please provide a username.")
                return
            #check that the desired username is available (not case sensitive)
            database.cur.execute("SELECT * FROM playerTable WHERE username='%s';" % username)
            if database.cur.fetchone() == None:
                database.cur.execute("INSERT INTO playerTable (discordID, username, elo, rep, stats) VALUES (%s, '%s', %s, %s, '%s');" % (ctx.author.id, username, 1300, 100, json.dumps(PLAYER_STATS_DICT)))
                database.conn.commit()
                await bot.guild.get_member(ctx.author.id).edit(nick=username)
                await ctx.author.add_roles(bot.guild.get_role(bot.MEMBER_ROLE))
                await ctx.author.add_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
                await ctx.author.send("You have been suggessfully registered. Welcome to CGL!")
            else:
                await ctx.send("The username %s is not available. Please choose another one to register for CGL." % username)
        else:
            await ctx.send("You have already registered for CGL.")

    @commands.command(pass_context=True)
    async def changename(self, ctx, username):
        """change username"""
        if database.user_registered(ctx.author.id):
            if username == None:
                await ctx.send("Please provide a new username.")
                return
            #check that the desired username is available (not case sensitive)
            database.cur.execute("SELECT * FROM playerTable WHERE username='%s';" % username)
            if database.cur.fetchone() == None:
                database.cur.execute("UPDATE playerTable SET username='%s' WHERE discordID=%s;" % (username, ctx.author.id))
                database.conn.commit()
                await bot.guild.get_member(ctx.author.id).edit(nick=username)
                await ctx.send("Username successfully changed.")
            else:
                await ctx.author.send("The username %s is not available. Please choose another one to register for CGL." % username)
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def report(self, ctx, target: CGLUser, *, reason):
        """reports another player's behaviour
        Reports another player's behavior. The player can be specified by one of two methods:
            mentioning the player or
            giving the player's full Discord tag.
        A reason must be provided after the player who is being reported."""
        if database.user_registered(ctx.author.id):
            if reason == None:
                await ctx.send("Please provide a reason for reporting the player.")
            await ctx.send("Report submitted for %s." % target.mention)
            await bot.guild.get_channel(bot.REPORTS_CHANNEL).send("%s reported %s for: %s" % (ctx.author.mention, target.mention, reason))
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

bot.add_cog(General())
