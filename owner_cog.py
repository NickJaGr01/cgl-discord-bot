from discord.ext import commands
import discord
from bot import bot
import database
from cgl_converters import *

NOT_OWNER_MESSAGE = "This command is only for use by the owner."

class Owner:
    @commands.command(pass_context=True)
    async def giveelo(self, ctx, target: CGLUser, delo: int):
        """change a player's elo"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            elo = database.player_elo(target.id)
            elo += delo
            database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (elo, target.id))
            database.conn.commit()
            await ctx.send("%s has been given %s elo." % (target.mention, delo))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def awardteam(self, ctx, team: CGLTeam, *, award):
        """give a team and its players an award"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("UPDATE teamTable SET awards=array_append(awards, '%s') WHERE teamname='%s';" % (award, team.teamname))
            database.cur.execute("UPDATE playerTable SET awards=array_append(awards, '%s') WHERE team='%s';" % (award, team.teamname))
            database.conn.commit()
            await ctx.send("%s and all its players have been awarded %s." % (team.teamname, award))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def awardplayer(self, ctx, player: CGLUser, *, award):
        """give a player an award"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("UPDATE playerTable SET awards=array_append(awards, '%s') WHERE discordID=%s;" % (award, player.id))
            database.conn.commit()
            await ctx.send("%s has been awarded %s." % (database.username(player.id), award))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

bot.add_cog(Owner())
