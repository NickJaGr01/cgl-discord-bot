import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

def user_registered(ctx):
    cur.execute("SELECT * FROM playerTable WHERE discordID=%s;" % ctx.author.id)
    return (cur.fetchone() != None)

def player_elo(discordID):
    cur.execute("SELECT elo FROM playerTable WHERE discordID=%s;" % discordID)
    return cur.fetchone()

def player_rep(discordID):
    cur.execute("SELECT rep FROM playerTable WHERE discordID=%s;" % discordID)
    return cur.fetchone()
