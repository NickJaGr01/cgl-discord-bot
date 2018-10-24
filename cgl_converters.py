import discord
from discord.ext import commands
import database
from bot import bot

class CGLUser(commands.UserConverter):
    async def convert(cls, ctx, argument):
        user = None
        try:
            user = await super().convert(ctx, argument)
        except:
            pass
        if user == None:
            database.cur.execute("SELECT discordID FROM playerTable WHERE username='%s';" % argument)
            discordid = database.cur.fetchone()
            if discordid != None:
                user = bot.get_user(discordid[0])
        if user != None:
            if database.user_registered(user.id):
                database.cur.execute("SELECT username FROM playerTable WHERE discordID=%s;" % user.id)
                user.CGL_name = database.cur.fetchone()[0]
        return user
