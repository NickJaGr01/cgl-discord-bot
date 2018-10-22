import database
from bot import bot
import os

CGL_server = int(os.environ['CGL_SERVER'])
FREE_AGENT_ROLE = 503654821644206093

async def process_invite(reaction, user):
    if reaction.message.author.id == bot.appinfo.id:
        if reaction.message.content.startswith("You have been invited to join"):
            team = reaction.message.content[30:-40]
            validreaction = False
            if reaction.emoji == u"\U0001F44D": #thumbsup
                validreaction = True
                database.cur.execute("UPDATE playerTable SET team='%s' WHERE discordID=%s;" % (team, user.id))
                database.cur.execute("SELECT teamRoleID FROM teamTable WHERE teamname='%s';" % team)
                roleid = database.cur.fetchone()[0]
                guild = bot.get_guild(CGL_server)
                teamrole = guild.get_role(roleid)
                member = guild.get_member(user.id)
                await member.add_roles(teamrole)
                #await member.remove_roles(guild.get_role(FREE_AGENT_ROLE))
                await user.send("You have joined team '%s'." % team)
                database.cur.execute("SELECT captainID FROM teamTable WHERE teamname='%s';" % team)
                captainID = database.cur.fetchone()[0]
                captain = bot.get_user(captainID)
                await captain.send("%s has accepted your team invite." % user.mention)
                database.conn.commit()
            elif reaction.emoji == u"\U0001F44E": #thumbsdown
                validreaction = True
                await user.send("You have declined the team invite.")
                database.cur.execute("SELECT captainID FROM teamTable WHERE teamname='%s';" % team)
                captainID = database.cur.fetchone()[0]
                captain = bot.get_user(captainID)
                await captain.send("%s declined your team invite." % user.mention)
            if validreaction:
                await reaction.message.delete()
