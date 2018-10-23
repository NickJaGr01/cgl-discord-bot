from bot import bot
from discord.ext import commands
import discord
import database
import json

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

class Teams:
    @commands.command(pass_context=True)
    async def createteam(self, ctx, *, teamname):
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
            teamrole = await bot.guild.create_role(name=teamname, colour=discord.Colour.orange(), hoist=True)
            #await teamrole.edit(position=bot.guild.get_role(bot.FREE_AGENT_ROLE).position+1)
            await teamrole.edit(position=1)
            #await bot.guild.get_member(ctx.author.id).add_roles(teamrole)
            database.cur.execute("INSERT INTO teamTable (teamname, stats, captainID, teamRoleID) VALUES ('%s', '%s', %s, %s);" % (teamname, json.dumps(TEAM_STATS_DICT), ctx.author.id, teamrole.id))
            database.cur.execute("UPDATE playerTable SET team='%s' WHERE discordID=%s;" % (teamname, ctx.author.id))
            database.conn.commit()
            await ctx.send("Team \'%s\' successfully created. Invite other players to your team using the !invite command." % teamname)
        else:
            await ctx.author.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def invite(self, ctx, player: discord.User):
        """invite a player to your team
        Invites another player to your team. The player can be specified by one of two methods:
            mentioning the player or
            giving the player's full Discord tag."""
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
            await ctx.send("%s has been invited to %s." % (bot.guild.get_member(player.id).nick, team))
        else:
            await ctx.author.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def leaveteam(self, ctx):
        """leaves your current team
        The captain of a team is not allowed to leave a team if there are other players on it.
        If the user is the last remaining player on the team, the team will be disbanded."""
        if database.user_registered(ctx.author.id):
            #check that the user is on a team
            database.cur.execute("SELECT team FROM playerTable WHERE discordID=%s;" % ctx.author.id)
            team = database.cur.fetchone()[0]
            if team == None:
                await ctx.send("You are not on a team.")
                return
            #check if there are other members on the team
            database.cur.execute("SELECT * FROM playerTable WHERE team='%s';" % team)
            othermembers = (len(database.cur.fetchall()) > 1)
            if not othermembers:
                database.cur.execute("SELECT teamRoleID FROM teamTable WHERE teamname='%s';" % team)
                roleid = database.cur.fetchone()[0]
                teamrole = bot.guild.get_role(roleid)
                database.cur.execute("DELETE FROM teamTable WHERE teamname='%s';" % team)
                database.cur.execute("UPDATE playerTable SET team=NULL WHERE team='%s';" % team)
                database.conn.commit()
                member = bot.guild.get_member(ctx.author.id)
                await member.remove_roles(teamrole)
                await member.add_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
                await ctx.send("Team '%s' has been disbanded." % team)
                return
            #check if the user is the captain of the team
            database.cur.execute("SELECT * FROM teamTable WHERE captainID=%s;" % ctx.author.id)
            if database.cur.fetchone() != None:
                await ctx.send("You cannot leave your team as the captain.\nPlease make another player the captain of the team before leaving.")
                return
            database.cur.execute("UPDATE playerTable SET team=NULL WHERE discordID=%s;" % ctx.author.id)
            database.conn.commit()
            await ctx.send("You have left team '%s'." % team)
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def disbandteam(self, ctx):
        """disbands the user's team if they are the captain"""
        if database.user_registered(ctx.author.id):
            #check that the user is on a team
            database.cur.execute("SELECT teamname FROM teamTable WHERE captainID=%s;" % ctx.author.id)
            team = database.cur.fetchone()
            if team == None:
                await ctx.send("You are not the captain of a team.")
                return
            team = team[0]
            database.cur.execute("SELECT teamRoleID FROM teamTable WHERE teamname='%s';" % team)
            roleid = database.cur.fetchone()[0]
            teamrole = bot.guild.get_role(roleid)
            database.cur.execute("DELETE FROM teamTable WHERE teamname='%s';" % team)
            database.cur.execute("SELECT discordID FROM playerTable WHERE team='%s';" % team)
            playerids = database.cur.fetchall()
            database.cur.execute("UPDATE playerTable SET team=NULL WHERE team='%s';" % team)
            database.conn.commit()
            for entry in playerids:
                member = bot.guild.get_member(entry[0])
                await member.remove_roles(teamrole)
                #await member.add_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
                await bot.get_user(entry[0]).send("Team '%s' has been disbanded by the team captain.\nYou are now a free agent." % team)
            await ctx.send("Team '%s' has been disbanded ." % team)
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

bot.add_cog(Teams())
