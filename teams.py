from bot import bot

async def process_invite(reaction, user):
    if reaction.message.author.id = bot.appinfo.id:
        if reaction.message.content.startswith("You have been invited to join"):
            team = reaction.message.content[30:-40]
            print("team = %s" % team)
