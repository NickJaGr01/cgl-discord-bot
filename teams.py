import database
from bot import bot

class Team:
    def __init__(self, teamname):
        self.teamname = teamname
        self.players = []
        self.region = None

    def add_player(self, player):
        self.players.append(player)

async def process_invite(reaction, user):
    if reaction.message.author.id == bot.appinfo.id:
        if reaction.message.content.startswith("You have been invited to join"):
            team = reaction.message.content[30:-40]
            validreaction = False
            if reaction.emoji == u"\U0001F44D": #thumbsup
                validreaction = True
                #check that there aren't too many players on the team
                database.cur.execute("SELECT * FROM playerTable WHERE team='%s';" % team)
                if len(database.cur.fetchall()) >= 7:
                    await user.send("You can no longer join that team because it has reached the maximum of 7 players.")
                else:
                    database.cur.execute("UPDATE playerTable SET team='%s' WHERE discordID=%s;" % (team, user.id))
                    database.conn.commit()
                    database.cur.execute("SELECT teamRoleID FROM teamTable WHERE teamname='%s';" % team)
                    roleid = database.cur.fetchone()[0]
                    teamrole = bot.guild.get_role(roleid)
                    member = bot.guild.get_member(user.id)
                    await member.add_roles(teamrole)
                    await member.remove_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
                    await user.send("You have joined team '%s'." % team)
                    database.cur.execute("SELECT captainID FROM teamTable WHERE teamname='%s';" % team)
                    captainID = database.cur.fetchone()[0]
                    captain = bot.get_user(captainID)
                    await captain.send("%s has accepted your team invite." % user.mention)
            elif reaction.emoji == u"\U0001F44E": #thumbsdown
                validreaction = True
                await user.send("You have declined the team invite.")
                database.cur.execute("SELECT captainID FROM teamTable WHERE teamname='%s';" % team)
                captainID = database.cur.fetchone()[0]
                captain = bot.get_user(captainID)
                await captain.send("%s declined your team invite." % user.mention)
            if validreaction:
                await reaction.message.delete()
