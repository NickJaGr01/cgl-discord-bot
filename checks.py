from bot import bot
from discord.ext import commands
import discord
import database

def is_registered():
    async def predicate(ctx):
        reg = database.user_registered(ctx.author.id)
        if not reg:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)
        return reg
    return commands.check(predicate)

def is_captain():
    async def predicate(ctx):
        database.cur.execute("SELECT * FROM teamTable WHERE captainID=%s;" % ctx.author.id)
        return database.cur.fetchone() != None
    return commands.check(predicate)
