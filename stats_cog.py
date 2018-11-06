from bot import bot
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
        info += "**Awards**:"
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
        info = "__%s__\n**Players**:\n" % team.teamname
        for p in team.players:
            info += "    %s\n" % database.username(p.id)
        info += "**Region**: %s\n" % team.region
        info += "**Awards**:"
        for award in team.awards:
            info += "\n    %s" % award
        await ctx.send(info)


bot.add_cog(Stats())
