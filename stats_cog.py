from bot import bot
from discord.ext import commands
import discord
import database

class Stats:
    @commands.command(pass_context=True)
    async def elo(ctx):
        """displays the player's elo."""
        if database.user_registered(ctx.author.id):
            await ctx.send("Your current elo is %s." % database.player_elo(ctx.author.id))
        else:
            await ctx.send(NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def rep(ctx):
        """displays the player's rep."""
        if database.user_registered(ctx.author.id):
            await ctx.send("Your current rep is %s." % database.player_rep(ctx.author.id))
        else:
            await ctx.send(NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def info(ctx, target):
        pass

bot.add_cog(Stats())