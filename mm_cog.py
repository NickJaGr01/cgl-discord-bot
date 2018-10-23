from bot import bot
from discord.ext import commands
import discord
import database

class Matchmaking:
    @commands.command(pass_context=True)
    async def accept(self, ctx):
        """confirm a match
        Once a match is found for a player in the matchmaking queue, the player will be prompted to confirm the match.
        Use this command within 30 seconds in order to confirm a match."""
        if database.user_registered(ctx.author.id):
            #find the user in the queue
            if ctx.author.id in bot.mmqueue.queue:
                bot.mmqueue.queue[ctx.author.id]["confirmed"] = True
                await ctx.author.send("You have accepted your game.\nWaiting for remaining players...")
            else:
                await ctx.author.send("You are not in the queue. You can join it by connecting to the matchmaking channel.")
        else:
            await ctx.author.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def commend(self, ctx, target: discord.User):
        """commends a player
        Gives the specified player +1 rep. The player can be specified by one of two methods:
            mentioning the player or
            giving the player's full Discord tag.
        This can be done once per match and must be done before reporting the match result."""
        if database.user_registered(ctx.author.id):
            if target == None:
                await ctx.send("That is not a valid player.")
                return
            #find the user in a lobby
            inmatch = False
            match = None
            for m in bot.matches:
                for id in bot.matches[m]["players"]:
                    if id == ctx.author.id:
                        inmatch = True
                        match = m
                        break
                if inmatch:
                    break
            if inmatch:
                if target.id != ctx.author.id:
                    if ctx.author.id not in bot.matches[match]["commendations"]:
                        if target.id in bot.matches[match]["players"]:
                            rep = database.player_rep(target.id)
                            rep += 1
                            database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, target.id))
                            database.conn.commit()
                            bot.matches[match]["commendations"].append(ctx.author.id)
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
            await ctx.author.send(bot.NOT_REGISTERED_MESSAGE)

bot.add_cog(Matchmaking())
