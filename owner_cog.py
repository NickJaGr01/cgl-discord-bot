from discord.ext import commands
import discord
from bot import bot
from utils import *
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
            targetusername = database.username(target.id)
            await ctx.send("%s has been given %s elo." % (targetusername, delo))
            await log("OWNER: %s gave %s rep to %s." % (database.username(ctx.author.id), drep, targetusername))
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
            await log("OWNER: %s gave the award %s to %s." % (database.username(ctx.author.id), award, team.teamname))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def awardplayer(self, ctx, player: CGLUser, *, award):
        """give a player an award"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("UPDATE playerTable SET awards=array_append(awards, '%s') WHERE discordID=%s;" % (award, player.id))
            database.conn.commit()
            targetusername = database.username(player.id)
            await ctx.send("%s has been awarded %s." % (targetusername, award))
            await log("OWNER: %s gave the award %s to %s." % (database.username(ctx.author.id), award, targetusername))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def setsponsorad(self, ctx, *, ad):
        """set the sponsor advertisement"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("UPDATE settings SET string='%s' WHERE key='sponsor_ad';" % (award, player.id))
            await ctx.send("The sponsor advertisement has been updated.")
            await log("OWNER: the sponsor advertisement has been updated:\n%s" % ad)
            announcements = bot.guild.get_channel(bot.ANNOUNCEMENTS_CHANNEL)
            database.cur.execute("SELECT int FROM settings WHERE key='last_ad_id';")
            lastad = database.cur.fetchone()[0]
            if lastad != None:
                await announcements.get_message(lastad).delete()
            if len(ad) > 0:
                newmsg = await announcements.send(ad)
                database.cur.execute("UPDATE settings SET int=%s WHERE key='last_sponsor_id';" % newmsg.id)
            database.conn.commit()
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def dostuff(self, ctx):
        """do stuff"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("SELECT teamname FROM teamTable;")
            teams = database.cur.fetchall()
            for team in teams:
                database.cur.execute("SELECT * FROM playerTable WHERE team='%s';" % team[0])
                if len(database.cur.fetchall()) <= 5:
                    database.cur.execute("UPDATE playerTable SET isPrimary=true WHERE team='%s';" % team[0])
            database.conn.commit()
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

bot.add_cog(Owner())
