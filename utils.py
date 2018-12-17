from bot import bot
import discord
from discord.ext import commands
import socket
import database

async def log(msg):
    await bot.guild.get_channel(bot.LOG_CHANNEL).send(msg)

def ip_from_domain(domain):
    return socket.gethostbyname(domain)

def escape_string(str):
    str.replace("'", "\\'")

def get_ingame_roles(discordid):
    player = bot.guild.get_member(discordid)
    r = []
    for role in player.roles:
        if role.id in bot.PLAYER_ROLE_ROLES.values():
            r.append(role.name)
    return r
