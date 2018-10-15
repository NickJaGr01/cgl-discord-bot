from discord.ext import commands
import discord
from datetime import datetime
from datetime import timedelta

import database
from bot import bot

CGL_server = 495761319639646208

MOD_ROLE = bot.get_guild(CGL_server).get_role(501438451284049920)
NOT_MOD_MESSAGE = "That command is only for use by CGL moderators."

MAJOR_OFFENSE_TABLE = {
    "length of suspension": [timedelta(minutes=2), timedelta(hours=6), timedelta(hours=24), timedelta(days=3), timedelta(days=7)],
    "rep penalty": [15, 30, 50, 80, 120]
}

@bot.command()
async def majoroffense(ctx, target: discord.User):
    if ctx.message.author.top_role >= MOD_ROLE:
        now = datetime.now()
        database.cur.execute("SELECT number_of_suspensions FROM playerTable WHERE discordID=%s;" % target.id)
        nofsuspensions = database.cur.fetchone()[0] + 1
        database.cur.execute("UPDATE playerTable SET number_of_suspensions=%s WHERE discordID=%s;" % (nofsuspensions, target.id))
        nofsuspensions = min(nofsuspensions, 5)
        suspension = MAJOR_OFFENSE_TABLE["length of suspension"][nofsuspensions-1]
        endofsuspension = now + suspension
        database.cur.execute("UPDATE playerTable SET end_of_suspension=%s WHERE discordID=%s;" % (end_of_suspension, target.id))
        reppen = MAJOR_OFFENSE_TABLE["rep penalty"][nofsuspensions-1]
        rep = database.player_rep(target.id) - reppen
        database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, target.id))
        database.conn.commit()
        await target.send("Due to a major offense, you have received a penalty of -%s rep and have been suspended from CGL matchmaking for %s." % (reppen, suspension))
    else:
        await ctx.send(NOT_MOD_MESSAGE)
