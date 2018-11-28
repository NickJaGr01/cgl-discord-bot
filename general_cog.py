from discord.ext import commands
import os
import discord
import database
from bot import bot
import utils
import json
from cgl_converters import *
from datetime import datetime
from datetime import timedelta

PLAYER_STATS_DICT = {
    "maps": {
        "dust2": {"wins": 0, "total": 0},
        "mirage": {"wins": 0, "total": 0},
        "cache": {"wins": 0, "total": 0},
        "inferno": {"wins": 0, "total": 0},
        "nuke": {"wins": 0, "total": 0},
        "overpass": {"wins": 0, "total": 0},
        "inferno": {"wins": 0, "total": 0}
    }
}

class General:
    @commands.command(pass_context=True)
    async def register(self, ctx, username):
        """register as a member in the league
        Before players can participate in league activities, they must register for the league.
        Upon registration, the player's server nickname will be changed to the one given.
        The player will also be given the Member and Free Agent roles."""
        if not database.user_registered(ctx.author.id):
            if username == None:
                await ctx.send("Please provide a username.")
                return
            #check that the desired username is available (not case sensitive)
            database.cur.execute("SELECT * FROM playerTable WHERE lower(username)='%s';" % username.lower())
            if database.cur.fetchone() == None:
                await bot.guild.get_member(ctx.author.id).edit(nick=username)
                await ctx.author.add_roles(bot.guild.get_role(bot.MEMBER_ROLE))
                await ctx.author.add_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
                utils.escape_string(username)
                database.cur.execute("INSERT INTO playerTable (discordID, username, elo, rep, stats, awards, isprimary) VALUES (%s, '%s', %s, %s, '%s', '{}', false);" % (ctx.author.id, username, 1300, 100, json.dumps(PLAYER_STATS_DICT)))
                database.conn.commit()
                await ctx.author.send("You have been suggessfully registered. Welcome to CGL!")
                await utils.log("%s registered as %s." % (ctx.author.mention, username))
            else:
                await ctx.send("The username %s is not available. Please choose another one to register for CGL." % username)
        else:
            await ctx.send("You have already registered for CGL.")

    @commands.command(pass_context=True)
    async def changename(self, ctx, username):
        """change username"""
        if database.user_registered(ctx.author.id):
            if username == None:
                await ctx.send("Please provide a new username.")
                return
            oldname = database.username(ctx.author.id)
            #check that the desired username is available (not case sensitive)
            database.cur.execute("SELECT * FROM playerTable WHERE lower(username)='%s';" % username.lower())
            if database.cur.fetchone() == None:
                await bot.guild.get_member(ctx.author.id).edit(nick=username)
                utils.escape_string(username)
                database.cur.execute("UPDATE playerTable SET username='%s' WHERE discordID=%s;" % (username, ctx.author.id))
                database.conn.commit()
                await ctx.send("Username successfully changed.")
                await utils.log("%s changed their username to %s." % (oldname, username))
            else:
                await ctx.send("The username %s is not available. Please choose another one to register for CGL." % username)
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def enterstandin(self, ctx):
        """register the user as a stand-in player"""
        if database.user_registered(ctx.author.id):
            channel = bot.guild.get_channel(bot.STANDIN_CHANNEL)
            username = database.username(ctx.author.id)
            await channel.send("%s wants to be a standin." % ctx.author.mention)
            await ctx.send("You have successfully entered the tournament as a stand-in.\nLeague staff will let you know if a team is found for you.")
            await utils.log("%s registered as a stand-in player." % username)
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def setregion(self, ctx, region):
        """set your region"""
        if database.user_registered(ctx.author.id):
            if region == None:
                await ctx.send("Please specify either NA or EU.")
                return
            member = bot.guild.get_member(ctx.author.id)
            if region.lower() == "na":
                if bot.guild.get_role(bot.EU_ROLE) in member.roles:
                    await member.remove_roles(bot.guild.get_role(bot.EU_ROLE))
                await member.add_roles(bot.guild.get_role(bot.NA_ROLE))
                await utils.log("%s set their region to NA." % database.username(ctx.author.id))
            elif region.lower() == "eu":
                if bot.guild.get_role(bot.NA_ROLE) in member.roles:
                    await member.remove_roles(bot.guild.get_role(bot.NA_ROLE))
                await member.add_roles(bot.guild.get_role(bot.EU_ROLE))
                await utils.log("%s set their region to EU." % database.username(ctx.author.id))
            else:
                await ctx.send("That is not a valid region.")
                return
            await ctx.send("Your region has been set to %s." % region.upper())
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def setfaceitname(self, ctx, *, name):
        """set your FACEIT name and get the invite link for your region's FACEIT hub"""
        if database.user_registered(ctx.author.id):
            member = bot.guild.get_member(ctx.author.id)
            if bot.guild.get_role(bot.EU_ROLE) not in member.roles and bot.guild.get_role(bot.NA_ROLE) not in member.roles:
                await ctx.send("Please set your region first with !setregion NA/EU.")
                return
            if name == None:
                await ctx.send("Please specify your FACEIT name.")
                return
            database.cur.execute("UPDATE playerTable SET faceitname='%s' WHERE discordID=%s;" % (name, ctx.author.id))
            database.conn.commit()
            invitelink = ""
            if bot.guild.get_role(bot.NA_ROLE) in member.roles:
                invitelink = bot.NA_HUB
            if bot.guild.get_role(bot.EU_ROLE) in member.roles:
                invitelink = bot.EU_HUB
            await ctx.author.send("Your FACEIT name has been set to %s.\n Use this link to join the FACEIT hub:\n%s\nDO NOT share this link under ANY circumstances." % (name, invitelink))
            await utils.log("%s set their FACEIT name to %s." % (database.username(ctx.author.id), name))
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def setroles(self, ctx, *roles):
        """set your player roles
        valid roles are AWPer, Rifler, IGL, Entry, Lurker, Support"""
        if database.user_registered(ctx.author.id):
            if roles == None:
                await ctx.send("Please specify your roles.")
                return
            member = bot.guild.get_member(ctx.author.id)
            badroles = ""
            goodroles = ""
            for r in bot.PLAYER_ROLE_ROLES.values():
                await member.remove_roles(bot.guild.get_role(r))
            for r in roles:
                if r.lower() not in bot.PLAYER_ROLE_ROLES:
                    badroles += "%s, " % r
                else:
                    role = bot.guild.get_role(bot.PLAYER_ROLE_ROLES[r.lower()])
                    await member.add_roles(role)
                    goodroles += "%s, " % role.name
            await ctx.send("Your roles have been updated.")
            if len(badroles) > 0:
                await ctx.send("The roles %s were not granted because they do not exist." % badroles[:-2])
            await utils.log("%s set their in-game roles to: %s" % (database.username(ctx.author.id), goodroles[:-2]))
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def commend(self, ctx, player: CGLUser):
        """commend another player
        """
        if database.user_registered(ctx.author.id):
            now = datetime.now()
            database.cur.execute("SELECT lastCommendTime FROM playerTable WHERE discordID=%s;" % ctx.author.id)
            lastcommend = database.cur.fetchone()[0]
            cancommend = False
            if lastcommend == None:
                cancommend = True
            else:
                duration = now - lastcommend
                if duration.total_seconds() >= 86400:
                    cancommend = True
                else:
                    await ctx.send("You have already commended someone within the last 24 hours.\nPlease try again later.")
            if cancommend:
                if player == None:
                    await ctx.send("That player does not exist.")
                    return
                if player.id == ctx.author.id:
                    await ctx.send("You cannot commend yourself.")
                    return
                database.cur.execute("SELECT team FROM playerTable WHERE discordID=%s;" % ctx.author.id)
                team = database.cur.fetchone()[0]
                if team != None:
                    database.cur.execute("SELECT team FROM playerTable WHERE discordID=%s;" % player.id)
                    if team == database.cur.fetchcone()[0]:
                        await ctx.send("You cannot commend one of your own teammates.")
                        return
                rep = database.player_rep(player.id)
                rep += 1
                database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, player.id))
                database.cur.execute("UPDATE playerTable SET lastCommendTime='%s' WHERE discordID=%s;" % (now, ctx.author.id))
                database.conn.commit()
                targetusername = database.username(player.id)
                await ctx.send("You have commended %s." % targetusername)
                await utils.log("%s commended %s." % (database.username(ctx.author.id), targetusername))
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

    @commands.command(pass_context=True)
    async def report(self, ctx, target: CGLUser, *, reason):
        """reports another player's behaviour
        Reports another player's behavior. The player can be specified by one of three methods:
            mentioning the player,
            giving the player's full Discord tag,
            the player's CGL username (or server specific nickname)
        A reason must be provided after the player who is being reported."""
        if database.user_registered(ctx.author.id):
            if target == None:
                await ctx.send("There was a problem identifying that player.")
                return
            if reason == None:
                await ctx.send("Please provide a reason for reporting the player.")
                return
            await ctx.send("Report submitted for %s." % target.mention)
            await bot.guild.get_channel(bot.REPORTS_CHANNEL).send("%s reported %s for: %s" % (ctx.author.mention, target.mention, reason))
        else:
            await ctx.send(bot.NOT_REGISTERED_MESSAGE)

bot.add_cog(General())
