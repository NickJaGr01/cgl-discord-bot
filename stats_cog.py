from bot import bot
from utils import *
from discord.ext import commands
import discord
import database
from cgl_converters import *
import math

class Stats:
    @commands.command(pass_context=True)
    async def elo(self, ctx):
        """displays the player's elo."""
        if database.user_registered(ctx.author.id):
            await ctx.send("Your current elo is %s." % database.player_elo(ctx.author.id))
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def rep(self, ctx):
        """displays the player's rep."""
        if database.user_registered(ctx.author.id):
            await ctx.send("Your current rep is %s." % database.player_rep(ctx.author.id))
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

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
        e.add_field(name="FACEIT", value=faceitname)
        team = database.player_team(player.id)
        if team == None:
            team = "*This player is not on a team.*"
        e.add_field(name="Team", value=team, inline=False)
        e.add_field(name="Elo", value=database.player_elo(player.id), inline=True).add_field(name="Rep", value=database.player_rep(player.id), inline=True)
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
            a = "*This player doesn't have any awards.*"
        e.add_field(name="Roles", value=r).add_field(name="Awards", value=a, inline=True)
        region = ""
        if bot.guild.get_role(bot.NA_ROLE) in player.roles:
            region = "🇺🇸 North America"
        if bot.guild.get_role(bot.EU_ROLE) in player.roles:
            region = "🇪🇺 Europe"
        if region == "":
            region = "*See* **!help setregion** *for more info.*"
        e.set_footer(text=region)
        await ctx.send("", embed=e)

    @commands.command(pass_context=True)
    async def teaminfo(self, ctx, *, team: CGLTeam):
        """display info about a team
        """
        if team == None:
            await ctx.send("That team does not exist.")
            return
        info = "__%s__\n" % team.teamname
        info += "**Primary**:\n"
        elo = 0
        teamsize = 0
        database.cur.execute("SELECT username, elo FROM playerTable WHERE team='%s' AND isPrimary=true;" % team.teamname)
        primary = database.cur.fetchall()
        for p in primary:
            info += "    %s\n" % p[0]
            elo += p[1]
            teamsize += 1
        info += "**Subs**:\n"
        database.cur.execute("SELECT username FROM playerTable WHERE team='%s' AND isPrimary=false;" % team.teamname)
        subs = database.cur.fetchall()
        for p in subs:
            info += "    %s\n" % p[0]
        if teamsize == 0:
            teamsize = 1
        elo = int(elo/teamsize)
        info += "**Team Elo**: %s\n" % elo
        info += "**Region**: %s\n" % team.region
        info += "**Awards**:"
        for award in team.awards:
            info += "\n    %s" % award
        await ctx.send(info)

    @commands.command(pass_context=True)
    async def teamlist(self, ctx, page: int = 1):
        """displays the top teams by elo 10
        10 teams per page"""
        page -= 1
        database.cur.execute("SELECT teamname, elo FROM teamtable ORDER BY elo DESC;")
        teams = database.cur.fetchall()
        teamcount = len(teams)
        rank = page*10
        start = rank
        end = rank+10
        if end >= teamcount:
            end = -1
        str = "__**Team - Elo:**__"
        for tname, telo in teams[rank:end]:
            rank += 1
            str += "\n%s) %s - %s" % (rank, tname, telo)
        str += "\n**Page %s of %s\nShowing %s-%s of %s**" % (page+1, math.ceil(teamcount/10), start, rank, teamcount)
        await ctx.send(str)

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
        database.cur.execute("SELECT username, %s FROM playerTable ORDER BY %s DESC;" % (stat, stat))
        players = database.cur.fetchall()
        playercount = len(players)
        rank = page*10
        start = rank
        end = rank+10
        if end >= playercount:
            end = -1
        str = "__**Player - %s:**__" % stat
        for username, ustat in players[rank:end]:
            rank += 1
            str += "\n%s) %s - %s" % (rank, username, ustat)
        str += "\n**Page %s of %s\nShowing %s-%s of %s**" % (page+1, math.ceil(playercount/10), start, rank, playercount)
        await ctx.send(str)

bot.add_cog(Stats())
