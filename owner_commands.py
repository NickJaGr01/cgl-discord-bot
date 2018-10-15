from discord.ext import commands
import discord
from bot import bot

import database

NOT_OWNER_MESSAGE = "This command is only for use by the owner."

@bot.command()
async def giveelo(ctx, target: discord.User, delo):
    if ctx.message.author.id == discord.AppInfo.owner.id:
        elo = database.player_elo(target.id)
        elo += delo
        database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (elo, target.id))
        database.conn.commit()
        await ctx.send("%s has been given %s elo points." % (target.mention, delo))
    else:
        await ctx.send(NOT_OWNER_MESSAGE)
