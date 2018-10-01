#import thread
import threading
import time
import discord
from discord.ext import commands
import os
import psycopg2
import database
import battle

bot = commands.Bot(command_prefix='!')
disabled=False

@bot.event
async def on_ready() :
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    #try :
    #    threading.Thread(target=bot_thread).start()
    #except :
    #    print('Error: unable to start thread')
    print('------')

@bot.command()
async def lobby(ctx):
    pass

token = os.environ['DISCORD_KEY']
bot.run(token)
