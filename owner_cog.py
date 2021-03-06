from discord.ext import commands
import discord
from bot import bot
import utils
import database
from cgl_converters import *
import servers
import checks
import teams
import matches

NOT_OWNER_MESSAGE = "This command is only for use by the owner."

class Owner:
    @commands.command(pass_context=True)
    @commands.is_owner()
    async def giveelo(self, ctx, delo: int, *players: CGLUser):
        """change a player's elo"""
        async with ctx.channel.typing():
            affectedteams = []
            for target in players:
                elo = database.player_elo(target.id)
                elo += delo
                database.cur.execute("UPDATE playerTable SET elo=%s WHERE discordID=%s;" % (elo, target.id))
                targetusername = database.username(target.id)
                await utils.log("OWNER: %s gave %s elo to %s." % (database.username(ctx.author.id), delo, targetusername))
                pteam = database.player_team(target.id)
                if pteam != None and pteam not in affectedteams:
                    affectedteams.append(pteam)
            database.conn.commit()
            for at in affectedteams:
                await teams.update_elo(at)
            await ctx.send("Those players have been given %s elo." % delo)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def awardteam(self, ctx, team: CGLTeam, *, award):
        """give a team and its players an award"""
        database.cur.execute("UPDATE teamTable SET awards=array_append(awards, '%s') WHERE teamname='%s';" % (award, team.teamname))
        database.cur.execute("UPDATE playerTable SET awards=array_append(awards, '%s') WHERE team='%s';" % (award, team.teamname))
        database.conn.commit()
        await ctx.send("%s and all its players have been awarded %s." % (team.teamname, award))
        await utils.log("OWNER: %s gave the award %s to %s." % (database.username(ctx.author.id), award, team.teamname))

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def awardplayer(self, ctx, player: CGLUser, *, award):
        """give a player an award"""
        database.cur.execute("UPDATE playerTable SET awards=array_append(awards, '%s') WHERE discordID=%s;" % (award, player.id))
        database.conn.commit()
        targetusername = database.username(player.id)
        await ctx.send("%s has been awarded %s." % (targetusername, award))
        await utils.log("OWNER: %s gave the award %s to %s." % (database.username(ctx.author.id), award, targetusername))

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def setsponsorad(self, ctx, *, ad):
        """set the sponsor advertisement"""
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

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def adjustelo(self, ctx, fillteam: bool, team1size: int, team1score: int, team2score: int, *players: CGLUser):
        """adjust stats after a match"""
        async with ctx.channel.typing():
            k_factor = 128
            affectedteams = []
            rounds = team1score+team2score
            team1avg = 0
            team2avg = 0
            for p in players[:team1size]:
                team1avg += database.player_elo(p.id)
                pteam = database.player_team(p.id)
                if pteam != None and pteam not in affectedteams:
                    affectedteams.append(pteam)
            for p in players[team1size:]:
                team2avg += database.player_elo(p.id)
                pteam = database.player_team(p.id)
                if pteam != None and pteam not in affectedteams:
                    affectedteams.append(pteam)
            team2size = len(players)-team1size
            if fillteam:
                team1avg += 1300 * (5-team1size)
                team2avg += 1300 * (5-team2size)
                team1avg /= 5
                team2avg /= 5
            else:
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
            for at in affectedteams:
                await teams.update_elo(at)
            await ctx.send("Elo has been updated for those players.")

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def creatematch(self, ctx, location, map, team1_name, team2_name, team1_size: int, *players: CGLUser):
        async with ctx.channel.typing():
            p = []
            for player in players:
                p.append(player.id)
            team1_players = p[:team1_size]
            team2_players = p[team1_size:]
            print(team1_players)
            match = matches.Match(team1_name, team1_players, team2_name, team2_players, map, location)
            matches.queue_match(match)
            server = matches.start_match(match)
            if server != None:
                ip = utils.ip_from_domain(server['ip'])
                await ctx.send("**game:** %s:%s" % (ip, server['ports']['game']))
            else:
                await ctx.send("Match could not be started.")

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def reportmatch(self, ctx, map, win: bool, *, team: CGLTeam):
        async with ctx.channel.typing():
            result = 1 if win else 0
            database.cur.execute("SELECT stats->'maps'->'%s'->>'wins' AS INTEGER FROM teamtable WHERE teamname='%s';" % (map, team))
            wins = database.cur.fetchone()
            database.cur.execute("SELECT stats ->'maps'->'%s'->>'total' AS INTEGER FROM teamtable WHERE teamname='%s';" % (map, team))
            total = database.cur.fetchone()
            wins += result
            total += 1
            database.cur.execute("UPDATE teamtable SET stats->'maps'->'%s'->>'wins'=%s, stats->'maps'->'%s'->>'total'=%s WHERE teamname='%s';"% (map, wins, map, total, team))
            database.conn.commit()
            await ctx.send("That team's stats have been updated.")

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def o_setfaceit(self, ctx, player: CGLUser, *, faceit):
        database.cur.execute("UPDATE playertable SET faceitname='%s' WHERE discordid=%s;" % (faceit, player.id))
        database.conn.commit()
        await ctx.send("That player's FACEIT has been updated.")
        await utils.log("OWNER: %s's FACEIT has been changed to <%s>" % (database.username(player.id), faceit))

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def o_cleanupleftplayers(self, ctx):
        async with ctx.channel.typing():
            database.cur.execute("SELECT discordid, username, team FROM playerTable;")
            allplayers = database.cur.fetchall()
            for id, name, team in allplayers:
                if bot.guild.get_member(id) == None:
                    if team != None:
                        database.cur.execute("UPDATE playertable SET team=NULL WHERE discordid=%s;" % id)
                        await ctx.send(name)
            database.conn.commit()
        await ctx.send("**Done**")

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def dostuff(self, ctx):
        """do stuff"""
        database.cur.execute("SELECT teamname, captainid FROM teamtable;")
        allteams = database.cur.fetchall()
        for team, captain in allteams:
            member = bot.guild.get_member(captain)
            if member == None:
                await teams.disband_team(team, "Your team has been disbanded because your captain has left the server.")
        await ctx.send("Done")

bot.add_cog(Owner())
