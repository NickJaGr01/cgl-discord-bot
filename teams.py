import database
from bot import bot

class Team:
    def __init__(self, teamname):
        self.teamname = teamname
        self.players = []
        self.region = None
        self.awards = []

    def add_player(self, player):
        self.players.append(player)

async def process_invite(reaction, user):
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
                database.cur.execute("UPDATE playerTable SET team='%s', isPrimary=false WHERE discordID=%s;" % (team, user.id))
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

async def process_roster_edit(reaction, user):
    emojis = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣"]
    if reaction.message.content.startswith("Please select your team's primary players"):
        if reaction.emoji == "✅":
            database.cur.execute("SELECT teamname FROM teamTable WHERE captainID=%s;" % user.id)
            team = database.cur.fetchone()
            database.cur.execute("SELECT discordID FROM playerTable WHERE team='%s';" % team)
            players = database.cur.fetchall()
            reactions = reaction.message.reactions
            subs = [p[0] for p in players]
            for r in reactions:
                if r.emoji in emojis:
                    index = emojis.index(r.emoji)
                    database.cur.execute("UPDATE playerTable SET isPrimary=true WHERE discordID=%s;" % players[index][0])
                    subs.remove(players[index][0])
            for s in subs:
                database.cur.execute("UPDATE playerTable SET isPrimary=false WHERE discordID=%s;" % s)
            await reaction.message.delete()
            await user.send("Your team's roster has been modified.")

async def disband_team(team, message):
    database.cur.execute("SELECT teamRoleID FROM teamTable WHERE teamname='%s';" % team)
    roleid = database.cur.fetchone()[0]
    teamrole = bot.guild.get_role(roleid)
    database.cur.execute("DELETE FROM teamTable WHERE teamname='%s';" % team)
    database.cur.execute("SELECT discordID FROM playerTable WHERE team='%s';" % team)
    playerids = database.cur.fetchall()
    database.cur.execute("UPDATE playerTable SET team=NULL WHERE team='%s';" % team)
    database.conn.commit()
    for entry in playerids:
        member = bot.guild.get_member(entry[0])
        await member.add_roles(bot.guild.get_role(bot.FREE_AGENT_ROLE))
        if message != None:
            await member.send(message)
    await teamrole.delete()
