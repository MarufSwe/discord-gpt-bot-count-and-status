import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai

load_dotenv()

discord_token = ""
intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

client = commands.Bot(command_prefix="/", intents=intents)
openai.api_key = ""

# Store guild and channel IDs
active_guilds = set()
active_channels = set()


def chatgpt_response(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=1,
        max_tokens=100
    )

    response_dict = response.get("choices")
    if response_dict and len(response_dict) > 0:
        prompt_response = response_dict[0]["text"]
        return prompt_response


async def user_count(guild):
    if guild:
        return len(guild.members)
    else:
        return 0


async def user_presence_status(guild):
    if guild:
        online_count = 0
        idle_count = 0
        offline_count = 0
        invisible_count = 0
        do_not_disturb_count = 0

        for member in guild.members:
            if member.status == discord.Status.online:
                online_count += 1
            elif member.status == discord.Status.idle:
                idle_count += 1
            elif member.status == discord.Status.invisible:
                invisible_count += 1
            elif member.status == discord.Status.dnd:
                do_not_disturb_count += 1
            else:
                offline_count += 1

        response = (
            f"Server Name: {guild.name}\n"
            f"Total members: {guild.member_count}\n"
            f"Online: {online_count}\n"
            f"Idle: {idle_count}\n"
            f"Invisible: {invisible_count}\n"
            f"Do not disturb: {do_not_disturb_count}\n"
            f"Offline: {offline_count}"
        )

        return response

    return "No guild found."


@client.event
async def on_ready():
    print("Successfully logged in as", client.user)
    print("Bot is ready!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    command, user_message = None, None

    for text in ['/', '/count', '/status']:
        if message.content.startswith(text):
            command = message.content.split(' ')[0]
            user_message = message.content.replace(text, '')
            break

    if command == '/':
        bot_response = chatgpt_response(prompt=user_message)
        await message.channel.send(bot_response)

    if command == '/count':
        guild = message.guild
        count = await user_count(guild)
        await message.channel.send(f"The server has {count} members.")

    if command == '/status':
        guild = message.guild
        presence_status = await user_presence_status(guild)
        await message.channel.send(presence_status)

    # Store guild and channel IDs
    active_guilds.add(message.guild.id)
    print('message.guild.id=======: ', message.guild.id)
    active_channels.add(message.channel.id)
    print('message.channel.id=======: ', message.channel.id)


@client.command()
async def get_ids(ctx):
    guild_ids = ", ".join(str(guild_id) for guild_id in active_guilds)
    channel_ids = ", ".join(str(channel_id) for channel_id in active_channels)

    response = (
        f"Active Guild IDs: {guild_ids}\n"
        f"Active Channel IDs: {channel_ids}"
    )
    await ctx.send(response)

client.run(discord_token)
