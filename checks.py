from bot import bot
from discord.ext import commands
import discord
import database

def is_registered():
    async def predicate(ctx):
        reg = database.user_registered(ctx.author.id)
        return reg
    return commands.check(predicate)

def not_registered():
    async def predicate(ctx):
        reg = database.user_registered(ctx.author.id)
        return not reg
    return commands.check(predicate)

def is_captain():
    async def predicate(ctx):
        database.cur.execute("SELECT * FROM teamTable WHERE captainID=%s;" % ctx.author.id)
        return database.cur.fetchone() != None
    return commands.check(predicate)

def on_team():
    async def predicate(ctx):
        database.cur.execute("SELECT team FROM playertable WHERE discordID=%s;" % ctx.author.id)
        team = database.cur.fetchone()
        if team == None:
            return False
        return team[0] != False
    return commands.check(predicate)
