from discord.ext import commands
import os
import discord
import database
from bot import bot
import json

NOT_REGISTERED_MESSAGE = "Please register before participating in CGL. You can register by using the \"!register *username*\" command."

REPORTS_CHANNEL = int(os.environ['REPORTS_CHANNEL'])

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

@bot.command()
async def register(ctx, username):
    """register as a member in the league
    Before players can participate in league activities, they must register for the league.
    Upon registration, the player's server nickname will be changed to the one given.
    The player will also be given the Member and Free Agent roles."""
    if not database.user_registered(ctx.author.id):
        #check that the desired username is available (not case sensitive)
        database.cur.execute("SELECT * FROM playerTable WHERE username='%s';" % username)
        if database.cur.fetchone() == None:
            if username == None:
                await ctx.send("Please provide a username.")
                return
            database.cur.execute("INSERT INTO playerTable (discordID, username, elo, rep, stats) VALUES (%s, '%s', %s, %s, '%s');" % (ctx.author.id, username, 1300, 100, json.dumps(PLAYER_STATS_DICT)))
            database.conn.commit()
            await ctx.author.send("You have been suggessfully registered. Welcome to CGL!")
            await ctx.author.edit(nick=username)
            await ctx.author.add_roles(bot.get_guild(CGL_server).get_role(MEMBER_ROLE))
            await ctx.author.add_roles(bot.get_guild(CGL_server).get_role(FREE_AGENT_ROLE))
        else:
            await ctx.author.send("The username %s is not available. Please choose another one to register for CGL." % username)
    else:
        await ctx.author.send("You have already registered for CGL.")

@bot.command()
async def report(ctx, target: discord.User, *, reason):
    """reports another player's behaviour
    Reports another player's behavior. The player can be specified by one of two methods:
        mentioning the player or
        giving the player's full Discord tag.
    A reason must be provided after the player who is being reported."""
    if database.user_registered(ctx.author.id):
        if reason == None:
            await ctx.send("Please provide a reason for reporting the player.")
        await ctx.send("Report submitted for %s." % target.mention)
        await bot.get_guild(CGL_server).get_channel(REPORTS_CHANNEL).send("%s reported %s for: %s" % (ctx.author.mention, target.mention, reason))
    else:
        await ctx.send(NOT_REGISTERED_MESSAGE)
