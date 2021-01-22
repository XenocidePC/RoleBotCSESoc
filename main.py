import os
import time
import discord
from discord.ext import commands
from discord.utils import get
from config.reaction_roles import reaction_roles

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)
ROLE_CHANNEL_ID = 0
ROLELOG_CHANNEL_ID = 0

@client.event
async def on_ready():
    print("Logged on as {0}!".format(client.user))


@client.event
async def on_message(message):
    try:
        # Check if the message is in the roles channel, and delete it after completion
        if message.channel.id == ROLE_CHANNEL_ID:
            await client.process_commands(message)
            await message.delete(2)
        else:
            await client.process_commands(message)
    except:
        time.sleep(1.2)
        await message.delete()


# Clear multiple messages in a channel at once, up to 10 at a time.
@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, count=3):
    if count > 10:
        count = 10
    await ctx.channel.purge(limit=count)


#Set role channel.
@client.command()
@commands.has_permissions(administrator=True)
async def setrole(ctx):
    global ROLE_CHANNEL_ID
    ROLE_CHANNEL_ID = ctx.channel.id
    await ctx.send(f"Set <#{ROLE_CHANNEL_ID}> as default role channel.")
    print(f"Set {ROLE_CHANNEL_ID} as default role channel")


# Set role log channel.
@client.command()
@commands.has_permissions(administrator=True)
async def setrolelog(ctx):
    global ROLELOG_CHANNEL_ID
    ROLELOG_CHANNEL_ID = ctx.channel.id
    await ctx.send(f"Set <#{ROLELOG_CHANNEL_ID}> as default role log channel.")
    print(f"Set {ROLELOG_CHANNEL_ID} as default role log channel")


# Give user a role.
@client.command()
async def give(ctx, *role_inputs):
    global ROLELOG_CHANNEL_ID
    logchannel = client.get_channel(ROLELOG_CHANNEL_ID)
    user = ctx.message.author
    message = ctx.message
    success = True
    if message.channel.id == ROLE_CHANNEL_ID:
        for role_input in role_inputs:
            role_input = role_input.upper()
            try:
                role = get(ctx.guild.roles, name=role_input)
                await user.add_roles(role)
                await ctx.send(f"✅ Gave {role_input} to {user}")
                await logchannel.send(f"✅ Gave {role_input} to {user}")
            except:
                await ctx.send(f"❌ Failed to give {role_input} to {user}. Please make sure your course code matches exactly e.g. `COMP1511` not `COMP 1511`")
                await logchannel.send(f"❌ Failed to give {role_input} to {user}")
                success = False
        if success:
            await ctx.message.add_reaction("👍")


# Take away user"s role.
@client.command()
async def remove(ctx, *role_inputs):
    global ROLELOG_CHANNEL_ID
    logchannel = client.get_channel(ROLELOG_CHANNEL_ID)
    user = ctx.message.author
    message = ctx.message
    success = True
    if message.channel.id == ROLE_CHANNEL_ID:
        for role_input in role_inputs:
            role_input = role_input.upper()
            try:
                role = get(ctx.guild.roles, name=role_input)
                await user.remove_roles(role)
                await ctx.send(f"✅ Removed {role_input} from {user}")
                await logchannel.send(f"✅ Removed {role_input} from {user}")
            except:
                await ctx.send(f"❌ Failed to remove {role_input} from {user}. Please make sure your course code matches exactly e.g. `COMP1511` not `COMP 1511`")
                await logchannel.send(f"❌ Failed to remove {role_input} from {user}")
                success = False
        if success:
            await ctx.message.add_reaction("👍")


@client.command()
@commands.has_permissions(administrator=True)
async def reactionrole(ctx, *role_inputs):
    embed = discord.Embed(title="Role Menu", description="React to give yourself a role")
    embed.add_field(name="COMP Level 1", value="```"
                                                "0️⃣ COMP1511\n"
                                                "1️⃣ COMP1521\n"
                                                "2️⃣ COMP1531"
                                                "```")
    embed.add_field(name="COMP Level 2", value="```"
                                                "3️⃣ COMP2041\n"
                                                "4️⃣ COMP2511\n"
                                                "5️⃣ COMP2521"
                                                "```")
    embed.add_field(name="MATH Level 1", value="```"
                                                "6️⃣ MATH1081\n"
                                                "7️⃣ MATH1131\n"
                                                "8️⃣ MATH1141\n"
                                                "9️⃣ MATH1231\n"
                                                "🔟 MATH1241"
                                                "```")
    rolemenu = await ctx.send(embed=embed)
    await rolemenu.add_reaction("0️⃣")
    await rolemenu.add_reaction("1️⃣")
    await rolemenu.add_reaction("2️⃣")
    await rolemenu.add_reaction("3️⃣")
    await rolemenu.add_reaction("4️⃣")
    await rolemenu.add_reaction("5️⃣")
    await rolemenu.add_reaction("6️⃣")
    await rolemenu.add_reaction("7️⃣")
    await rolemenu.add_reaction("8️⃣")
    await rolemenu.add_reaction("9️⃣")
    await rolemenu.add_reaction("🔟")


async def process_reaction(payload, action):
    if payload.message_id in reaction_roles.keys():
        for item in reaction_roles[payload.message_id]:
            if item[0] == payload.emoji.name:
                guild = client.get_guild(payload.guild_id)
                user = await guild.fetch_member(payload.user_id)
                role = guild.get_role(item[1])
                if role is None:
                    print(f"Invalid role ({item[0]}, {item[1]}) provided in reaction_roles.py"
                          f"for message with ID: {payload.message_id}")
                elif action == "add":
                    await user.add_roles(role)
                elif action == "remove":
                    await user.remove_roles(role)
                break


@client.event
async def on_raw_reaction_add(payload):
    await process_reaction(payload, "add")


@client.event
async def on_raw_reaction_remove(payload):
    await process_reaction(payload, "remove")


client.run(os.environ["DISCORD_BOT_TOKEN"])
