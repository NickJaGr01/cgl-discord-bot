import discord
from discord.ext import commands
import database
from bot import bot

class CGLUser(commands.MemberConverter):
    async def convert(cls, ctx, argument):
        try:
            member = await super().convert(ctx, argument)
            return member
        except:
            database.cur.execute("SELECT discordID FROM playerTable WHERE username='%s';" % argument)
            discordid = database.cur.fetchone()
            if discordid != None:
                return bot.guild.get_member(discordid[0])
        return None
