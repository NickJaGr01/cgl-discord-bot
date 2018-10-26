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
            database.cur.execute("SELECT discordID FROM playerTable WHERE username='%s';" % argument)
            discordid = database.cur.fetchone()
            if discordid != None:
                return bot.guild.get_member(discordid[0])
        return None

class CGLTeam(commands.Converter):
    async def convert(cls, ctx, argument):
        database.cur.execute("SELECT teamname, captainID FROM teamTable WHERE teamname='%s';" % argument)
        data = database.cur.fetchone()
        if data == None:
            #could not find team
            return None
        teamname = data[0]
        team = Team(teamname)
        captainID = data[1]
        database.cur.execute("SELECT username FROM playerTable WHERE team='%s';" % teamname)
        members = database.cur.fetchall()
        for id in members:
            team.add_player(bot.guild.get_member(id[0]))
        captain = bot.guild.get_member(captainID)
        if bot.guild.get_role(bot.NA_ROLE) in captain.roles:
            team.region = "NA"
        if bot.guild.get_role(bot.EU_ROLE) in captain.roles:
            team.region = "EU"
        return team
