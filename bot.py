#import thread
import threading
import time
import discord
from discord.ext import commands
import os
import psycopg2
import math

from mm import *

NOT_REGISTERED_MESSAGE = "Please register before participating in CGL. You can register by using the \"!register *username*\" command."

bot = commands.Bot(command_prefix='!')

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

mmqueue = MMQueue()
matches = {}

available_lobbies = [i for i in range(20)]

def user_registered(ctx):
    cur.execute("SELECT * FROM playerTable WHERE discordID=%s;" % ctx.author.id)
    return (cur.fetchone() != None)

def bot_thread():
    while True:
        cycle_queue()

def cycle_queue():
    inq = mmqueue.in_queue()
    lobby = 0
    for i in range(math.floor(len(inq)/10)*10):
        if i%10 == 0:
            if len(available_lobbies) == 0:
                break
            lobby = available_lobbies[0]
            available_lobbies.pop(0)
        id = inq[i]
        team = 0
        if i%10/5 >= 1:
            team = 1
        mmqueue.move(id, lobby, team)
        user = bot.get_user(id)
        user.send("A game has been found! Type \"!accept\" to confirm.")
        user.send("30 seconds left")
    mmqueue.step_time()
    lobbies = mmqueue.lobbies()
    for l in lobbies.keys():
        ready = True
        for id in lobbies[l]["players"]:
            if not lobbies[l]["players"][id]["confirmed"]:
                ready = False
                user = bot.get_user(id)
                user.send("%s" % lobbies[l]["time"])
        if ready:
            matches[l] = {}
            for id in lobbies[l]["players"]:
                matches[l][id] = {"team": mmqueue.queue[id]["team"]}
            continue

        if lobbies[l]["time"] <= 0:
            for id in lobbies[l]["players"]:
                if lobbies[l]["players"][id]["confirmed"]:
                    mmqueue.move(id, -1)
                    user = bot.get_user(id)
                    user.send("One or more players in your lobby failed to confirm the match. You have been added back to the queue.")
                else:
                    del mmqueue.queue[id]
                    mmqueue.pop(id)
                    user = bot.get_user(id)
                    user.send("You failed to confirm your match. You have been removed from the queue.")
            available_lobbies.append(l)

    time.sleep(1)

@bot.event
async def on_ready() :
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    try :
        threading.Thread(target=bot_thread).start()
    except :
        print('Error: unable to start thread')

@bot.command()
async def register(ctx, username):
    if not user_registered(ctx):
        #check that the desired username is available (not case sensitive)
        cur.execute("SELECT * FROM playerTable WHERE username='%s';" % username)
        if cur.fetchone() == None:
            cur.execute("INSERT INTO playerTable (discordID, username) VALUES (%s, '%s');" % (ctx.author.id, username))
            conn.commit()
            await ctx.author.send("You have been suggessfully registered. Welcome to CGL!")
        else:
            await ctx.author.send("The username %s is not available. Please choose another one to register for CGL." % username)
    else:
        await ctx.author.send("You have already registered for CGL.")

@bot.command()
async def accept(ctx):
    if user_registered(ctx):
        #find the user in the queue
        for e in mmqueue:
            if e[0].id == ctx.author.id:
                if e[1] == 0:
                    return
                if e[1] < 0:
                    e[1] *= -1
                    await ctx.author.send("You have accepted your game.\nWaiting for remaining players...")
                return
        await ctx.author.send("You are not in the queue. You can join it by typing \"!queue\"")
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def queue(ctx):
    if user_registered(ctx):
        mmqueue.push(ctx.author.id)
        await ctx.author.send("You have been added to the queue.\nPlayers in queue: %s" % len(queue.in_queue()))
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def lobby(ctx, lobby_link):
    pass

token = os.environ['DISCORD_KEY']
bot.run(token)
