import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai
from datetime import datetime, timedelta

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


async def last_day_message_count(channel):
    # Get the current date
    current_date = datetime.utcnow().date()
    # Calculate the start and end times for the current date
    start_time = datetime.combine(current_date, datetime.min.time())
    end_time = datetime.combine(current_date, datetime.max.time())

    # Count the messages within the time range
    total_messages = 0
    async for message in channel.history(after=start_time, before=end_time):
        total_messages += 1

    if total_messages > 0:
        return f"Total messages today: {total_messages}"
    else:
        return "No messages found today."


async def last_week_message_count(channel):  # with today
    # Get the current date and time
    current_datetime = datetime.utcnow()

    # Calculate the start and end times for the last week
    start_time = current_datetime - timedelta(weeks=1)
    end_time = current_datetime

    # Count the messages within the time range using pagination
    total_messages = 0
    async for message in channel.history(limit=None, after=start_time, before=end_time):
        total_messages += 1

    # Add the count of new messages sent after the function is called
    async for message in channel.history(limit=None, after=end_time):
        total_messages += 1

    if total_messages > 0:
        return f"Total messages from the last week: {total_messages}"
    else:
        return "No messages found today."


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

    # for text in ['/', '/count', '/status']:
    for text in ['/ai', '/count', '/status', '/day', '/week']:
        if message.content.startswith(text):
            command = message.content.split(' ')[0]
            user_message = message.content.replace(text, '')
            break

    if command == '/ai':
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

    if command == '/day':
        channel = message.channel
        message_count = await last_day_message_count(channel)
        await message.channel.send(message_count)

    if command == '/week':
        channel = message.channel
        message_count = await last_week_message_count(channel)
        await message.channel.send(message_count)

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
