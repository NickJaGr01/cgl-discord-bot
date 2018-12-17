from bot import bot

async def process_get_roles(reaction, user):
    if reaction.message.content.startswith("Please select your roles"):
        if reaction.emoji == "✅":
            member = bot.guild.get_member(user.id)
            reactions = reaction.message.reactions
            for r in reactions:
                if r.emoji in bot.LIST_EMOJIS:
                    index = bot.LIST_EMOJIS.index(r.emoji)
                    role = bot.PLAYER_ROLE_ROLES.values()[index]
                    if r.count == 2:
                        if role not in member.roles:
                            await member.add_roles(role)
                    elif r.count == 1:
                        if role in member.roles:
                            await member.remove_roles(role)
            await reaction.message.delete()
            await user.send("Your roles have been updated")
