from discord.ext import commands
import os
import discord
import database
from bot import bot
from bot import CGL_server
from matchmaking import mmqueue
from matchmaking import matches
import json

NOT_REGISTERED_MESSAGE = "Please register before participating in CGL. You can register by using the \"!register *username*\" command."

REPORTS_CHANNEL = int(os.environ['REPORTS_CHANNEL'])

MEMBER_ROLE = 499276055585226773
FREE_AGENT_ROLE = 503654821644206093

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

TEAM_STATS_DICT = {
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
async def createteam(ctx, *, teamname):
    """create a team
    Creates a new team with the given name and makes the user the captain of that team.
    Players may not create a team if they are already a member of another team."""
    if database.user_registered(ctx.author.id):
        #check that the user is not already on a team
        database.cur.execute("SELECT team FROM playerTable WHERE discordID=%s;" % ctx.author.id)
        if database.cur.fetchone()[0] != None:
            await ctx.send("You cannot be on more than one team at a time. Please leave your current team before creating another one.")
            return
        if teamname == None:
            await ctx.send("Please provide a team name.")
            return
        #create the team
        guild = bot.get_guild(CGL_server)
        teamrole = await guild.create_role(name=teamname, colour=discord.Colour.orange(), hoist=True)
        await teamrole.edit(position=guild.get_role(FREE_AGENT_ROLE).position+1)
        await guild.get_member(ctx.author.id).add_roles(teamrole)
        database.cur.execute("INSERT INTO teamTable (teamname, stats, captainID, teamRoleID) VALUES ('%s', '%s', %s, %s);" % (teamname, json.dumps(TEAM_STATS_DICT), ctx.author.id, teamrole.id))
        database.cur.execute("UPDATE playerTable SET team='%s' WHERE discordID=%s;" % (teamname, ctx.author.id))
        database.conn.commit()
        await ctx.send("Team \'%s\' successfully created. Invite other players to your team using the !invite command." % teamname)
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def invite(ctx, player: discord.User):
    if database.user_registered(ctx.author.id):
        #make sure the user is the captain of a team
        database.cur.execute("SELECT teamname FROM teamTable WHERE captainID=%s;" % ctx.author.id)
        team = database.cur.fetchone()[0]
        if team == None:
            await ctx.send("You are not a captain of a team.")
            return
        #make sure the target player isn't already on a team
        database.cur.execute("SELECT team FROM playerTable WHERE discordID=%s;" % player.id)
        targetteam = database.cur.fetchone()
        if targetteam == None:
            await ctx.send("That player is not a member of the league.")
            return
        if targetteam[0] != None:
            await ctx.send("That player is already on a team.")
            return
        invite = await player.send("You have been invited to join %s.\n:thumbsup: accept\n:thumbsdown: decline" % team)
        await invite.add_reaction(u"\U0001F44D") #thumbsup
        await invite.add_reaction(u"\U0001F44E") #thumbsdown
        await ctx.send("%s has been invited to %s." % (bot.get_guild(CGL_server).get_member(player.id).nick, team))
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def accept(ctx):
    """confirm a match
    Once a match is found for a player in the matchmaking queue, the player will be prompted to confirm the match.
    Use this command within 30 seconds in order to confirm a match."""
    if database.user_registered(ctx.author.id):
        #find the user in the queue
        if ctx.author.id in mmqueue.queue:
            mmqueue.queue[ctx.author.id]["confirmed"] = True
            await ctx.author.send("You have accepted your game.\nWaiting for remaining players...")
        else:
            await ctx.author.send("You are not in the queue. You can join it by connecting to the matchmaking channel.")
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def elo(ctx):
    """displays the player's elo."""
    if database.user_registered(ctx.author.id):
        await ctx.send("Your current elo is %s." % database.player_elo(ctx.author.id))
    else:
        await ctx.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def rep(ctx):
    """displays the player's rep."""
    if database.user_registered(ctx.author.id):
        await ctx.send("Your current rep is %s." % database.player_rep(ctx.author.id))
    else:
        await ctx.send(NOT_REGISTERED_MESSAGE)

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

@bot.command()
async def commend(ctx, target: discord.User):
    """commends a player
    Gives the specified player +1 rep. The player can be specified by one of two methods:
        mentioning the player or
        giving the player's full Discord tag.
    This can be done once per match and must be done before reporting the match result."""
    if database.user_registered(ctx.author.id):
        if target == None:
            await ctx.send("That is not a valid player.")
            return
        #find the user in a lobby
        inmatch = False
        match = None
        for m in matches:
            for id in matches[m]["players"]:
                if id == ctx.author.id:
                    inmatch = True
                    match = m
                    break
            if inmatch:
                break
        if inmatch:
            if target.id != ctx.author.id:
                if ctx.author.id not in matches[match]["commendations"]:
                    if target.id in matches[match]["players"]:
                        rep = database.player_rep(target.id)
                        rep += 1
                        database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, target.id))
                        database.conn.commit()
                        matches[match]["commendations"].append(ctx.author.id)
                        await ctx.send("You commended %s." % target.mention)
                        await target.send("Someone commended you. You have gained 1 rep.")
                    else:
                        await ctx.send("You can only commend someone who is in the same match as you are.")
                else:
                    await ctx.send("You can only commend one other player per match.")
            else:
                await ctx.send("You cannot commend yourself")
        else:
            await ctx.send("You are not currently in a match. You cannot commend anyone.")
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)
