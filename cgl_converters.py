import discord
from discord.ext import commands
import database
from bot import bot

class CGLUser(commands.UserConverter):
    async def convert(cls, ctx, argument):
        try:
            user = await super().convert(ctx, argument)
            return user
        except:
            database.cur.execute("SELECT discordID FROM playerTable WHERE username='%s';" % argument)
            discordid = database.cur.fetchone()
            if discordid != None:
                return bot.get_user(discordid[0])
