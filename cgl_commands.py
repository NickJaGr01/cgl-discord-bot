from discord.ext import commands
import os
import discord
import database
from bot import bot
from bot import CGL_server
from matchmaking import mmqueue
from matchmaking import matches

NOT_REGISTERED_MESSAGE = "Please register before participating in CGL. You can register by using the \"!register *username*\" command."

REPORTS_CHANNEL = int(os.environ['REPORTS_CHANNEL'])

@bot.command()
async def register(ctx, username):
    if not database.user_registered(ctx):
        #check that the desired username is available (not case sensitive)
        database.cur.execute("SELECT * FROM playerTable WHERE username='%s';" % username)
        if database.cur.fetchone() == None:
            database.cur.execute("INSERT INTO playerTable (discordID, username, elo, rep) VALUES (%s, '%s', %s, %s);" % (ctx.author.id, username, 1300, 100))
            database.conn.commit()
            await ctx.author.send("You have been suggessfully registered. Welcome to CGL!")
            await ctx.author.edit(nick=username)
            await ctx.author.add_roles(bot.get_guild(CGL_server).get_role(499276055585226773))
        else:
            await ctx.author.send("The username %s is not available. Please choose another one to register for CGL." % username)
    else:
        await ctx.author.send("You have already registered for CGL.")

@bot.command()
async def accept(ctx):
    if database.user_registered(ctx):
        #find the user in the queue
        if ctx.author.id in mmqueue.queue:
            mmqueue.queue[ctx.author.id]["confirmed"] = True
            await ctx.author.send("You have accepted your game.\nWaiting for remaining players...")
        else:
            await ctx.author.send("You are not in the queue. You can join it by connecting to the matchmaking channel.")
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def elo(ctx):
    if database.user_registered(ctx):
        await ctx.send("Your current elo is %s." % database.player_elo(ctx.author.id))
    else:
        await ctx.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def rep(ctx):
    if database.user_registered(ctx):
        await ctx.send("Your current rep is %s." % database.player_rep(ctx.author.id))
    else:
        await ctx.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def report(ctx, target: discord.User, *, reason):
    if database.user_registered(ctx):
        await ctx.send("Report submitted for %s." % target.mention)
        await bot.get_guild(CGL_server).get_channel(REPORTS_CHANNEL).send("%s reported %s for: %s" % (ctx.author.mention, target.mention, reason))
    else:
        await ctx.send(NOT_REGISTERED_MESSAGE)

@bot.command()
async def commend(ctx, target: discord.User):
    if database.user_registered(ctx):
        if target == None:
            await ctx.send("That is not a valid player.")
            return
        #find the user in a lobby
        inmatch = False
        match = None
        for m in matches:
            for id in matches[m]["players"]:
                if id == ctx.author.id:
                    inmatch = True
                    match = m
                    break
            if inmatch:
                break
        if inmatch:
            if target.id != ctx.author.id:
                if ctx.author.id not in matches[match]["commendations"]:
                    if target.id in matches[match]["players"]:
                        rep = database.player_rep(target.id)
                        rep += 1
                        database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, target.id))
                        database.conn.commit()
                        matches[match]["commendations"].append(ctx.author.id)
                        await ctx.send("You commended %s." % target.mention)
                        await target.send("Someone commended you. You have gained 1 rep.")
                    else:
                        await ctx.send("You can only commend someone who is in the same match as you are.")
                else:
                    await ctx.send("You can only commend one other player per match.")
            else:
                await ctx.send("You cannot commend yourself")
        else:
            await ctx.send("You are not currently in a match. You cannot commend anyone.")
    else:
        await ctx.author.send(NOT_REGISTERED_MESSAGE)
