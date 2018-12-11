import database
from bot import bot
import utils

class Team:
    def __init__(self, teamname):
        self.teamname = teamname
        self.players = []
        self.region = None
        self.awards = []
        self.captain = None

    def add_player(self, player):
        self.players.append(player)

async def process_standins():
    database.cur.execute("SELECT team, player, timeinvited FROM standinrequests;")
    requests = database.cur.fetchall()
    for team, player, timeinvited in requests:
        if player == None:
            pass
            #find stand-in player
            #database.cur.execute("SELECT discordID FROM playerTable WHERE ")


async def process_invite(reaction, user):
    if reaction.message.content.startswith("You have been invited to join"):
        team = reaction.message.content[30:-40]
        validreaction = False
        if reaction.emoji == u"\U0001F44D": #thumbsup
            validreaction = True
            targetusername = database.username(user.id)
            #check that there aren't too many players on the team
            database.cur.execute("SELECT * FROM playerTable WHERE team='%s';" % team)
            teamsize = len(database.cur.fetchall())
            if teamsize >= 7:
                await user.send("You can no longer join that team because it has reached the maximum of 7 players.")
                await utils.log("%s could not join %s. There are too many players." % (targetusername, team))
            else:
                isPrimary = 'false'
                if teamsize < 5:
                    isPrimary = 'true'
                database.cur.execute("UPDATE playerTable SET team='%s', isPrimary=%s WHERE discordID=%s;" % (team, isPrimary, user.id))
                database.conn.commit()
                await update_elo(team)
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
                await captain.send("%s has accepted your team invite." % targetusername)
                await utils.log("%s joined %s." % (targetusername, team))
        elif reaction.emoji == u"\U0001F44E": #thumbsdown
            validreaction = True
            await user.send("You have declined the team invite.")
            database.cur.execute("SELECT captainID FROM teamTable WHERE teamname='%s';" % team)
            captainID = database.cur.fetchone()[0]
            captain = bot.get_user(captainID)
            await captain.send("%s declined your team invite." % targetusername)
            await utils.log("%s declined an invite to %s." % (targetusername, team))
        if validreaction:
            await reaction.message.delete()

async def process_roster_edit(reaction, user):
    emojis = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣"]
    if reaction.message.content.startswith("Please select your team's primary players"):
        if reaction.emoji == "✅":
            database.cur.execute("SELECT teamname FROM teamTable WHERE captainID=%s;" % user.id)
            team = database.cur.fetchone()[0]
            database.cur.execute("SELECT discordID FROM playerTable WHERE team='%s';" % team)
            players = database.cur.fetchall()
            reactions = reaction.message.reactions
            primary = []
            subs = [p[0] for p in players]
            for r in reactions:
                if r.emoji in emojis:
                    if r.count == 2:
                        index = emojis.index(r.emoji)
                        primary.append(players[index][0])
                        subs.remove(players[index][0])
            if len(primary) > 5:
                await user.send("You cannot have more than 5 primary players on a team. Please try again.")
                await reaction.message.delete()
                return
            for p in primary:
                database.cur.execute("UPDATE playerTable SET isPrimary=true WHERE discordID=%s;" % p)
            for s in subs:
                database.cur.execute("UPDATE playerTable SET isPrimary=false WHERE discordID=%s;" % s)
            database.conn.commit()
            await update_elo(team)
            await reaction.message.delete()
            await user.send("Your team's roster has been modified.")
            await utils.log("%s modified %s's roster." % (database.username(user.id), team))

async def order_team_roles():
    database.cur.execute("SELECT teamroleID FROM teamtable ORDER BY elo DESC;")
    roles = database.cur.fetchall()
    pos = bot.guild.get_role(bot.TEAMS_BOTTOM_END_ROLE).position + 1
    for r in roles:
        role = bot.guild.get_role(r[0])
        if role == None:
            continue
        await role.edit(position=pos)
    await utils.log("Team role heirarchy has been updated.")

async def update_role_position(team):
    database.cur.execute("SELECT elo, teamroleid FROM teamtable WHERE teamname='%s';" % team)
    teamelo, trole = database.cur.fetchone()
    trole = bot.guild.get_role(trole)
    database.cur.execute("SELECT teamroleid FROM teamtable WHERE elo<%s ORDER BY elo DESC;" % teamelo)
    rolebelow = database.cur.fetchone()
    if rolebelow == None:
        rolebelow = bot.TEAMS_BOTTOM_END_ROLE
    else:
        rolebelow = rolebelow[0]
    rolebelow = bot.guild.get_role(rolebelow)
    await trole.edit(position=rolebelow.position+1)
    await utils.log("%s's role position has been updated." % team)


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
    await utils.log("%s has been disbanded." % team)

async def update_elo(team):
    database.cur.execute("SELECT elo FROM playertable WHERE team='%s';" % team)
    elos = database.cur.fetchall()
    total = 0
    teamsize = 0
    for p in elos:
        total += p[0]
        teamsize += 1
    average = total / teamsize
    if teamsize < 5:
        makeup = 5 - teamsize
        for x in range(makeup):
            total += min(1200, average)
            teamsize += 1
        average = total / teamsize
    database.cur.execute("UPDATE teamtable SET elo=%s WHERE teamname='%s';" % (average, team))
    database.conn.commit()
    await update_role_position(team)
    return average
