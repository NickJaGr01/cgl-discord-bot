import discord
from discord.ext import commands
import database
from bot import bot
from teams import Team

class CGLUser(commands.MemberConverter):
    async def convert(cls, ctx, argument):
        try:
            member = await super().convert(ctx, argument)
            return member
        except:
            database.cur.execute("SELECT discordID FROM playerTable WHERE lower(username)='%s';" % argument.lower())
            discordid = database.cur.fetchone()
            if discordid != None:
                return bot.guild.get_member(discordid[0])
        return None

class CGLTeam(commands.RoleConverter):
    async def convert(cls, ctx, argument):
        teamname = None
        try:
            trole = await super().convert(ctx, argument)
            database.cur.execute("SELECT teamname FROM teamTable WHERE teamroleid=%s;" % trole.id)
            teamname = database.cur.fetchone()
            if teamname == None:
                return None
            teamname = teamname[0]
        except:
            database.cur.execute("SELECT teamname FROM teamTable WHERE lower(teamname)='%s';" % argument.lower())
            teamname = database.cur.fetchone()
            if teamname == None:
                return None
            teamname = teamname[0]
        database.cur.execute("SELECT teamname, captainID FROM teamTable WHERE teamname='%s';" % teamname)
        data = database.cur.fetchone()
        team = Team(teamname)
        captainID = data[1]
        team.captain = captainID
        database.cur.execute("SELECT discordID FROM playerTable WHERE team='%s';" % teamname)
        members = database.cur.fetchall()
        for id in members:
            team.add_player(bot.guild.get_member(id[0]))
        captain = bot.guild.get_member(captainID)
        if bot.guild.get_role(bot.NA_ROLE) in captain.roles:
            team.region = "NA"
        elif bot.guild.get_role(bot.EU_ROLE) in captain.roles:
            team.region = "EU"
        database.cur.execute("SELECT awards FROM teamTable WHERE teamname='%s';" % teamname)
        team.awards = database.cur.fetchone()[0]
        return team
