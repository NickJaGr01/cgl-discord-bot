from discord.ext import commands
import discord
from datetime import datetime
from datetime import timedelta
import os
import database
from bot import bot
from cgl_converters import *

MOD_ROLE_ID = int(os.environ['MOD_ROLE'])
NOT_MOD_MESSAGE = "That command is only for use by CGL moderators."

MAJOR_OFFENSE_TABLE = {
    "length of suspension": [timedelta(minutes=30), timedelta(hours=6), timedelta(hours=24), timedelta(days=3), timedelta(days=7)],
    "rep penalty": [15, 30, 50, 80, 120]
}

class Admin:
    @commands.command(pass_context=True)
    async def giverep(self, ctx, target: CGLUser, drep: int):
        """modify a player's rep"""
        modrole = bot.guild.get_role(MOD_ROLE_ID)
        if ctx.message.author.top_role >= modrole:
            if target == None:
                await ctx.send("There was an error identifying that player.")
                return
            if drep == None:
                await ctx.send("Please provide an amount of rep to give.")
                return
            rep = database.player_rep(target.id)
            rep += drep
            database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, target.id))
            database.conn.commit()
            await ctx.send("%s has been given %s rep." % (database.username(target.id), drep))
        else:
            await ctx.send(NOT_MOD_MESSAGE)

    @commands.command(pass_context=True)
    async def majoroffense(self, ctx, target: CGLUser):
        """administer a major offense penalty"""
        modrole = bot.guild.get_role(MOD_ROLE_ID)
        if ctx.message.author.top_role >= modrole:
            now = datetime.now()
            database.cur.execute("SELECT number_of_suspensions FROM playerTable WHERE discordID=%s;" % target.id)
            nofsuspensions = database.cur.fetchone()[0] + 1
            database.cur.execute("UPDATE playerTable SET number_of_suspensions=%s WHERE discordID=%s;" % (nofsuspensions, target.id))
            nofsuspensions = min(nofsuspensions, 5)
            suspension = MAJOR_OFFENSE_TABLE["length of suspension"][nofsuspensions-1]
            endofsuspension = now + suspension
            database.cur.execute("UPDATE playerTable SET end_of_suspension=\'%s\' WHERE discordID=%s;" % (endofsuspension, target.id))
            reppen = MAJOR_OFFENSE_TABLE["rep penalty"][nofsuspensions-1]
            rep = database.player_rep(target.id) - reppen
            database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, target.id))
            database.conn.commit()
            await target.send("Due to a major offense, you have received a penalty of -%s rep and have been suspended from CGL matchmaking for %s." % (reppen, suspension))
        else:
            await ctx.send(NOT_MOD_MESSAGE)

bot.add_cog(Admin())
