from discord.ext import commands
import discord
import database
from bot import bot
from bot import CGL_server

NOT_REGISTERED_MESSAGE = "Please register before participating in CGL. You can register by using the \"!register *username*\" command."

@bot.command()
async def register(ctx, username):
    if not database.user_registered(ctx):
        #check that the desired username is available (not case sensitive)
        database.cur.execute("SELECT * FROM playerTable WHERE username='%s';" % username)
        if database.cur.fetchone() == None:
            database.cur.execute("INSERT INTO playerTable (discordID, username) VALUES (%s, '%s');" % (ctx.author.id, username))
            database.conn.commit()
            await ctx.author.send("You have been suggessfully registered. Welcome to CGL!")
            await ctx.author.edit(nick=username, roles=[CGL_server.get_role(499276055585226773)])
        else:
            await ctx.author.send("The username %s is not available. Please choose another one to register for CGL." % username)
    else:
        await ctx.author.send("You have already registered for CGL.")

@bot.command()
async def accept(ctx):
    if database.user_registered(ctx):
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
async def elo(ctx):
    if user_registered(ctx):
        await ctx.author.send("Your current elo is %s." % database.player_elo(ctx.author.id))
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)
