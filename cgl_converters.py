import discord
from discord.ext import commands
import database
from bot import bot

class CGLUser(commands.UserConverter):
    async def convert(cls, ctx, argument):
        user = await super().convert(ctx, argument)
        if user == None:
            database.cur.execute("SELECT discordID FROM playerTable WHERE username='%s';" % argument)
            discordid = database.cur.fetchone()
            if discordid == None:
                break
            user = bot.get_user(discordid[0])
        return user
