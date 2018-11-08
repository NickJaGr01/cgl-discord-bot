from bot import bot
import discord
from discord.ext import commands

async def log(msg):
    await bot.guild.get_channel(bot.LOG_CHANNEL).send(msg)
