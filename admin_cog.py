from discord.ext import commands
import discord
from datetime import datetime
from datetime import timedelta
import os
import database
from bot import bot
import utils
from cgl_converters import *
import servers

MOD_ROLE_ID = int(os.environ['MOD_ROLE'])
NOT_MOD_MESSAGE = "That command is only for use by CGL moderators."

MAJOR_OFFENSE_TABLE = {
    "length of suspension": [timedelta(minutes=30), timedelta(hours=6), timedelta(hours=24), timedelta(days=3), timedelta(days=7)],
    "rep penalty": [15, 30, 50, 80, 120]
}

class Admin:
    @commands.command(pass_context=True)
    @commands.has_role('Admin')
    async def giverep(self, ctx, drep: int, *players: CGLUser):
        """give rep to players"""
        if drep == None:
            await ctx.send("Please provide an amount of rep to give.")
            return
        goodplayers = ""
        badplayers = ""
        for p in players:
            if p == None:
                badplayers += "%s, " % database.username(p.id)
                continue
            else:
                goodplayers += "%s, " % database.username(p.id)
                rep = database.player_rep(p.id)
                rep += drep
                database.cur.execute("UPDATE playerTable SET rep=%s WHERE discordID=%s;" % (rep, p.id))
        database.conn.commit()
        if len(goodplayers) > 0:
            await ctx.send("%s have been given %s rep." % (goodplayers[:-1], drep))
            await utils.log("ADMIN: %s gave %s rep to %s." % (database.username(ctx.author.id), drep, goodplayers[:-1]))
        if len(badplayers) > 1:
            await ctx.send("%s were not given any rep because they do not exist." % badplayers[:-1])

    @commands.group(pass_context=True)
    @commands.has_role('Admin')
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use !help server for a list of subcommands.")
    @server.command(pass_context=True)
    @commands.is_owner()
    async def create(self, ctx, servername, location, map):
        database.cur.execute("SELECT * FROM servertable WHERE lower(servername)='%s';" % servername)
        if database.cur.fetchone() != None:
            await ctx.send("A server with that name already exists.")
            return
        server, scode = servers.create_server(name, location, map)
        if scode == 200:
            database.cur.execute("INSERT INTO servertable (servername, serverid, location, up) VALUES (%s, %s, %s, true);" % (servername, server['id'], location))
            database.conn.commit()
            await ctx.send("Server created.")
        else:
            await ctx.send("Server creation failed.")
    @server.command(pass_context=True)
    @commands.is_owner()
    async def delete(self, ctx, servername):
        database.cur.execute("SELECT serverid FROM servertable WHERE lower(servername)='%s';" % servername)
        id = database.cur.fetchone()
        if id == None:
            await ctx.send("No server with that name exists.")
            return
        id = id[0]
        scode = servers.delete_server(id)
        if scode == 200:
            database.cur.execute("DELETE FROM servertable WHERE serverid='%s';" % id)
            database.conn.commit()
            await ctx.send("Server has been deleted.")
        else:
            await ctx.send("The server could not be deleted.")
    @server.command(pass_context=True)
    @commands.has_role('Admin')
    async def list(self, ctx):
        serverlist, scode = servers.server_list()
        if scode == 200:
            str = "```\nserver name:        location:           up:\n"
            for server in serverlist:
                str += server['name']
                str = str.ljust(len(str)+(20-len(server['name'])))
                str += server['location']
                str = str.ljust(len(str)+(20-len(server['location'])))
                str += "%s\n" % server['on']
            str += "```"
            await ctx.send(str)
        else:
            await ctx.send("There was an error retrieving the server list.")
    @server.command(pass_context=True)
    @commands.has_role('Admin')
    async def info(self, ctx, servername):
        server, scode = servers.server_info(servers.server_id(servername))
        if scode == 200:
            str = "__**%s**__\n" % server['name']
            str += "**id:** %s\n" % server['id']
            str += "**location:** %s\n" % server['location']
            str += "**start map:** %s\n" % server['csgo_settings']['mapgroup_start_map']
            str += "**slots:** %s\n" % server['csgo_settings']['slots']
            str += "**up:** %s\n" % server['on']
            ip = utils.ip_from_domain(server['ip'])
            str += "**game:** %s:%s\n" % (ip, server['ports']['game'])
            str += "**gotv:** %s:%s" % (ip, server['ports']['gotv'])
            await ctx.send(str)
        else:
            await ctx.send("Failed to get server info.")
    @server.command(pass_context=True)
    @commands.has_role('Admin')
    async def start(self, ctx, servername):
        scode = servers.start_server(servers.server_id(servername))
        if scode == 200:
            await ctx.send("Server started.")
        else:
            await ctx.send("Failed to start server.")
    @server.command(pass_context=True)
    @commands.has_role('Admin')
    async def stop(self, ctx, servername):
        scode = servers.stop_server(servers.server_id(servername))
        if scode == 200:
            await ctx.send("Server stopped.")
        else:
            await ctx.send("Failed to stop server.")

    @server.group(pass_context=True)
    async def edit(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use !help server edit for a list of subcommands.")
    @edit.command(pass_context=True)
    @commands.has_role('Admin')
    async def map(self, ctx, servername, map):
        scode = servers.edit_server(servers.server_id(servername), {'csgo_settings.mapgroup_start_map':map})
        if scode == 200:
            await ctx.send("Server start map has been changed.")
        else:
            await ctx.send("There was an error editing the server settings.")
    @edit.command(pass_context=True)
    @commands.has_role('Admin')
    async def location(self, ctx, servername, location):
        scode = servers.edit_server(servers.server_id(servername), {'location':location})
        if scode == 200:
            await ctx.send("Server location has been changed.")
        else:
            await ctx.send("There was an error editing the server settings.")
    @edit.command(pass_context=True)
    @commands.has_role('Admin')
    async def name(self, ctx, servername, newname):
        scode = servers.edit_server(servers.server_id(servername), {'name':newname})
        if scode == 200:
            await ctx.send("Server name has been changed.")
        else:
            await ctx.send("There was an error editing the server settings.")
    @edit.command(pass_context=True)
    @commands.has_role('Admin')
    async def slots(self, ctx, servername, slots: int):
        scode = servers.edit_server(servers.server_id(servername), {'csgo_settings.slots':slots})
        if scode == 200:
            await ctx.send("Server size has been changed.")
        else:
            await ctx.send("There was an error editing the server settings.")


bot.add_cog(Admin())
