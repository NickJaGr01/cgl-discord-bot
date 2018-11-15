from discord.ext import commands
import discord
from bot import bot
import utils
import database
from cgl_converters import *
import servers

NOT_OWNER_MESSAGE = "This command is only for use by the owner."

class Owner:
    @commands.command(pass_context=True)
    async def giveelo(self, ctx, target: CGLUser, delo: int):
        """change a player's elo"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            elo = database.player_elo(target.id)
            elo += delo
            database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (elo, target.id))
            database.conn.commit()
            targetusername = database.username(target.id)
            await ctx.send("%s has been given %s elo." % (targetusername, delo))
            await utils.log("OWNER: %s gave %s rep to %s." % (database.username(ctx.author.id), drep, targetusername))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def awardteam(self, ctx, team: CGLTeam, *, award):
        """give a team and its players an award"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("UPDATE teamTable SET awards=array_append(awards, '%s') WHERE teamname='%s';" % (award, team.teamname))
            database.cur.execute("UPDATE playerTable SET awards=array_append(awards, '%s') WHERE team='%s';" % (award, team.teamname))
            database.conn.commit()
            await ctx.send("%s and all its players have been awarded %s." % (team.teamname, award))
            await utils.log("OWNER: %s gave the award %s to %s." % (database.username(ctx.author.id), award, team.teamname))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def awardplayer(self, ctx, player: CGLUser, *, award):
        """give a player an award"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("UPDATE playerTable SET awards=array_append(awards, '%s') WHERE discordID=%s;" % (award, player.id))
            database.conn.commit()
            targetusername = database.username(player.id)
            await ctx.send("%s has been awarded %s." % (targetusername, award))
            await utils.log("OWNER: %s gave the award %s to %s." % (database.username(ctx.author.id), award, targetusername))
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def setsponsorad(self, ctx, *, ad):
        """set the sponsor advertisement"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("UPDATE settings SET string='%s' WHERE key='sponsor_ad';" % (award, player.id))
            await ctx.send("The sponsor advertisement has been updated.")
            await utils.log("OWNER: the sponsor advertisement has been updated:\n%s" % ad)
            announcements = bot.guild.get_channel(bot.ANNOUNCEMENTS_CHANNEL)
            database.cur.execute("SELECT int FROM settings WHERE key='last_ad_id';")
            lastad = database.cur.fetchone()[0]
            if lastad != None:
                await announcements.get_message(lastad).delete()
            if len(ad) > 0:
                newmsg = await announcements.send(ad)
                database.cur.execute("UPDATE settings SET int=%s WHERE key='last_sponsor_id';" % newmsg.id)
            database.conn.commit()
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.command(pass_context=True)
    async def adjustelo(self, ctx, team1size: int, team1score: int, team2score: int, *players: CGLUser):
        """adjust elo after a match"""
        k_factor = 128
        if ctx.message.author.id == bot.appinfo.owner.id:
            rounds = team1score+team2score
            team1avg = 0
            team2avg = 0
            for p in players[:team1size]:
                team1avg += database.player_elo(p.id)
            for p in players[team1size:]:
                team2avg += database.player_elo(p.id)
            team1avg /= team1size
            team2avg /= team2size
            team1exp = 1/(1+pow(10, (team2avg-team1avg)/400))
            team2exp = 1/(1+pow(10, (team1avg-team2avg)/400))
            delo1 = k_factor * ((team1score/rounds) - team1exp)
            delo2 = k_factor * ((team2score/rounds) - team2exp)
            for p in players[:team1size]:
                elo = database.player_elo(p.id)
                elo += delo1
                database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (elo, p.id))
                await utils.log("%s has been given %s elo." % (database.username(p.id), delo1))
            for p in players[team1size:]:
                elo = database.player_elo(p.id)
                elo += delo2
                database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (elo, p.id))
                await utils.log("%s has been given %s elo." % (database.username(p.id), delo2))
            database.conn.commit()
            await ctx.send("Elo has been updated for those players.")
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

    @commands.group(pass_context=True)
    async def server(self, ctx):
        if ctx.message.author.id == bot.appinfo.owner.id:
            if ctx.invoked_subcommand is None:
                pass
        else:
            await ctx.send(NOT_OWNER_MESSAGE)
    @server.command(pass_context=True)
    async def list(self, ctx):
        database.cur.execute("SELECT servername, up FROM servertable;")
        serverlist = database.cur.fetchall()
        str = "```\nserver name         up\n"
        for name, up in serverlist:
            str += name
            str = str.ljust(len(str)+(20-len(name)))
            str += "%s\n" % up
        str += "```"
        await ctx.send(str)
    @server.command(pass_context=True)
    async def create(self, ctx, location, map):
        server = servers.create_server("CGL CSGO", location, map)
        print(server)
        await ctx.send("Server created.\nid=%s\nConnect to %s:%s" % (server['id'], server['ip'], server['ports']['game']))
    @server.command(pass_context=True)
    async def start(self, ctx, id):
        server = servers.start_server(id)
        await ctx.send("Server started.\nConnect to %s:%s" % (server['ip'], server['ports']['game']))
    @server.command(pass_context=True)
    async def stop(self, ctx, id):
        servers.stop_server(id)
        await ctx.send("Server stopped.")

    @commands.command(pass_context=True)
    async def dostuff(self, ctx):
        """do stuff"""
        if ctx.message.author.id == bot.appinfo.owner.id:
            database.cur.execute("SELECT teamname FROM teamTable;")
            teams = database.cur.fetchall()
            for team in teams:
                database.cur.execute("SELECT * FROM playerTable WHERE team='%s';" % team[0])
                if len(database.cur.fetchall()) <= 5:
                    database.cur.execute("UPDATE playerTable SET isPrimary=true WHERE team='%s';" % team[0])
            database.conn.commit()
        else:
            await ctx.send(NOT_OWNER_MESSAGE)

bot.add_cog(Owner())
