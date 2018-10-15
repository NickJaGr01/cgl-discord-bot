from discord.ext import commands
import discord
from bot import bot

import database

NOT_OWNER_MESSAGE = "This command is only for use by the owner."

@bot.command()
async def giveelo(ctx, target: discord.User, delo: int):
    if ctx.message.author.id == bot.appinfo.owner.id:
        elo = database.player_elo(target.id)
        elo += delo
        database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (elo, target.id))
        database.conn.commit()
        await ctx.send("%s has been given %s elo." % (target.mention, delo))
    else:
        await ctx.send(NOT_OWNER_MESSAGE)

@bot.command()
async def giverep(ctx, target: discord.User, drep: int):
    if ctx.message.author.id == bot.appinfo.owner.id:
        rep = database.player_rep(target.id)
        rep += drep
        database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, target.id))
        database.conn.commit()
        await ctx.send("%s has been given %s rep." % (target.mention, drep))
    else:
        await ctx.send(NOT_OWNER_MESSAGE)
