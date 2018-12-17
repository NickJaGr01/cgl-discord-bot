import os
import psycopg2
from bot import bot

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

def username(discordID):
    cur.execute("SELECT username FROM playerTable WHERE discordID=%s;" % discordID)
    return cur.fetchone()[0]

def user_registered(discordID):
    cur.execute("SELECT * FROM playerTable WHERE discordID=%s;" % discordID)
    return (cur.fetchone() != None)

def player_elo(discordID):
    cur.execute("SELECT elo FROM playerTable WHERE discordID=%s;" % discordID)
    return cur.fetchone()[0]

def team_elo(teamname):
    cur.execute("SELECT elo FROM teamtable WHERE teamname='%s';" % teamname)
    return cur.fetchone()[0]

def player_rep(discordID):
    cur.execute("SELECT rep FROM playerTable WHERE discordID=%s;" % discordID)
    return cur.fetchone()[0]

def player_team(discordID):
    cur.execute("SELECT team FROM playerTable WHERE discordID=%s;" % discordID)
    return cur.fetchone()[0]

def player_suspension(discordID):
    cur.execute("SELECT end_of_suspension FROM playerTable WHERE discordID=%s;" % discordID)
    return cur.fetchone()[0]

def get_ingame_roles(discordid):
    player = bot.guild.get_member(discordid)
    r = []
    for role in player.roles:
        if role.id in bot.PLAYER_ROLE_ROLES.values():
            r.append(role.name)
    return r
