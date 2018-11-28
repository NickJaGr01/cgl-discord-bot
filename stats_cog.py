from bot import bot
from utils import *
from discord.ext import commands
import discord
import database
from cgl_converters import *

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
        info = "__%s__\n" % database.username(player.id)
        database.cur.execute("SELECT faceitname FROM playerTable WHERE discordID=%s;" % player.id)
        faceitname = database.cur.fetchone()[0]
        info += "**FACEIT**: %s\n" % faceitname
        info += "**Elo**: %s\n" % database.player_elo(player.id)
        info += "**Rep**: %s\n" % database.player_rep(player.id)
        info += "**Team**: %s\n" % database.player_team(player.id)
        member = bot.guild.get_member(player.id)
        region = None
        if bot.guild.get_role(bot.NA_ROLE) in member.roles:
            region = "NA"
        if bot.guild.get_role(bot.EU_ROLE) in member.roles:
            region = "EU"
        info += "**Region**: %s\n" % region
        info += "**Roles**:"
        for role in member.roles:
            if role.id in bot.PLAYER_ROLE_ROLES.values():
                info += " %s" % role.name
        info += "\n**Awards**:"
        database.cur.execute("SELECT awards FROM playerTable WHERE discordID=%s;" % player.id)
        awards = database.cur.fetchone()[0]
        for award in awards:
            info += "\n    %s" % award

        await ctx.send(info)

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
    async def leaderboard(self, ctx, page: int = 1, sortby="elo"):
        """displays the top players, 10 per page
        valid stats to sort by are:
            elo
            rep
        by default, players are sorted by elo."""
        valid_sorts = ["elo", "rep"]
        if sortby.lower() not in valid_sorts:
            await ctx.send("%s is not a valid sort parameter. Use !help leaderboard for more info.")
        page -= 1
        database.cur.execute("SELECT username, %s FROM playerTable ORDER BY %s DESC;" % (sortby, sortby))
        players = database.cur.fetchall()
        str = "__**Player - %s:**__" % sortby
        rank = page*10
        for username, stat in players[page*10:page*10+10]:
            rank += 1
            str += "\n%s) %s - %s" % (rank, username, stat)
        str += "\n%s-%s of %s" % (rank-9, rank, len(players))
        await ctx.send(str)

bot.add_cog(Stats())
