from bot import bot
from utils import *
from discord.ext import commands
import discord
import database
from cgl_converters import *
import math

class Stats:
    @commands.command(pass_context=True)
    async def playerinfo(self, ctx, *, player: CGLUser):
        """display info about a player
        """
        if player == None:
            await ctx.send("That player does not exist.")
            return
        e = discord.Embed(title=database.username(player.id), description=player.mention, colour=discord.Colour.blue())
        database.cur.execute("SELECT faceitname FROM playerTable WHERE discordID=%s;" % player.id)
        faceitname = database.cur.fetchone()[0]
        if faceitname == None:
            faceitname = "*This player has not connected their FACEIT.*"
        e.add_field(name="FACEIT", value=faceitname)
        e.add_field(name="Elo", value=database.player_elo(player.id)).add_field(name="Rep", value=database.player_rep(player.id))
        team = database.player_team(player.id)
        if team == None:
            team = "*This player is not on a team.*"
        e.add_field(name="Team", value=team)
        r = ""
        for role in player.roles:
            if role.id in bot.PLAYER_ROLE_ROLES.values():
                if len(r) > 0:
                    r += "\n"
                r += role.name
        if r == "":
            r = "*See* **!help setroles** *for more info.*"
        database.cur.execute("SELECT awards FROM playerTable WHERE discordID=%s;" % player.id)
        awards = database.cur.fetchone()[0]
        a = ""
        for award in awards:
            if len(a) > 0:
                a += "\n"
            a += award
        if a == "":
            a = "*This player does not have any awards.*"
        e.add_field(name="Roles", value=r).add_field(name="Awards", value=a)
        region = ""
        if bot.guild.get_role(bot.NA_ROLE) in player.roles:
            region = "🇺🇸 North America"
        if bot.guild.get_role(bot.EU_ROLE) in player.roles:
            region = "🇪🇺 Europe"
        if region == "":
            region = "See '!help setregion' for more info."
        e.set_footer(text=region)
        await ctx.send("", embed=e)

    @commands.command(pass_context=True)
    async def teaminfo(self, ctx, *, team: CGLTeam):
        """display info about a team
        """
        if team == None:
            await ctx.send("That team does not exist.")
            return

        database.cur.execute("SELECT captainID FROM teamtable WHERE teamname='%s';" % team.teamname)
        captainid = database.cur.fetchone()[0]
        e = discord.Embed(title=team.teamname, description="Captain: %s" % database.username(captainid), colour=discord.Colour.blue())
        elo = 0
        teamsize = 0
        database.cur.execute("SELECT discordID, elo FROM playerTable WHERE team='%s' AND isPrimary=true;" % team.teamname)
        primary = database.cur.fetchall()
        pstr = ""
        for p in primary:
            if len(pstr) > 0:
                pstr += "\n"
            pstr += "%s" % bot.get_user(p[0]).mention
            elo += p[1]
            teamsize += 1
        e.add_field(name="Primary", value=pstr)
        database.cur.execute("SELECT discordID FROM playerTable WHERE team='%s' AND isPrimary=false;" % team.teamname)
        subs = database.cur.fetchall()
        sstr = ""
        for p in subs:
            if len(sstr) > 0:
                sstr += "\n"
            sstr += "%s" % bot.get_user(p[0]).mention
        e.add_field(name="Subs", value=sstr)
        if teamsize == 0:
            teamsize = 1
        elo = int(elo/teamsize)
        e.add_field(name="Team Elo", value=elo)
        astr = ""
        for award in team.awards:
            if len(astr) > 0:
                astr += "\n"
            astr += "%s" % award
        if len(astr) == 0:
            astr = "*This team does not have any awards.*"
        e.add_field(name="Awards", value=astr)
        rstr = "This team's captain has not set their region."
        captain = bot.guild.get_member(captainid)
        if bot.guild.get_role(bot.NA_ROLE) in captain.roles:
            rstr = "🇺🇸 North America"
        elif bot.guild.get_role(bot.EU_ROLE) in captain.roles:
            rstr = "🇪🇺 Europe"
        e.set_footer(text=rstr)
        await ctx.send(embed=e)

    @commands.command(pass_context=True)
    async def teamlist(self, ctx, page: int = 1):
        """displays the top teams by elo 10
        10 teams per page"""
        page -= 1
        database.cur.execute("SELECT teamname, elo FROM teamtable ORDER BY elo DESC;")
        teams = database.cur.fetchall()
        teamcount = len(teams)
        rank = page*10
        end = rank+10
        if end >= teamcount:
            end = -1
        e = discord.Embed(colour=discord.Colour.blue())
        str = ""
        for tname, telo in teams[rank:end]:
            rank += 1
            str += "\n%s) %s - %s" % (rank, tname, telo)
        e.add_field(name="Teams - Elo", value=str)
        e.set_footer(text="\nPage %s of %s" % (page+1, math.ceil(teamcount/10)))
        await ctx.send(embed=e)

    @commands.command(pass_context=True)
    async def leaderboard(self, ctx, stat="elo", page: int = 1):
        """displays the top players, 10 per page
        valid stats to sort by are:
            elo
            rep
        by default, players are sorted by elo."""

        valid_stats = ["elo", "rep"]
        if stat.lower() not in valid_stats:
            await ctx.send("%s is not a valid sort parameter. Use !help leaderboard for more info.")
        page -= 1
        database.cur.execute("SELECT discordID, %s FROM playerTable ORDER BY %s DESC;" % (stat, stat))
        players = database.cur.fetchall()
        playercount = len(players)
        rank = page*10
        end = rank+10
        if end >= playercount:
            end = -1
        e = discord.Embed(colour=discord.Colour.blue())
        str = ""
        for id, ustat in players[rank:end]:
            rank += 1
            str += "\n%s) %s - %s" % (rank, bot.get_user(id).mention, ustat)
        e.add_field(name="Leaderboard - %s" % stat, value=str)
        e.set_footer(text="Page %s of %s" % (page+1, math.ceil(playercount/10)))
        await ctx.send(embed=e)

bot.add_cog(Stats())
