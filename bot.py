# bot.py
import os

from discord.ext import commands
from dotenv import load_dotenv

from meeting import Meeting
from thread import Thread
from meeting_register import MeetingRegister

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")
meeting_register = MeetingRegister()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


@bot.command()
async def thread(ctx, *, args):
    # Check if user is a participant in any meetings
    meeting = meeting_register.get_meeting(ctx.author)
    if not meeting:
        raise ValueError("User not in a meeting")


    if args[0] == 'create':
        thread_name = ' '.join(args)
        thread = Thread(thread_name, ctx.author)
        thread.1
        return


    meeting_register.addThread(str(ctx.author))
    await ctx.send(str(ctx.author) + ' added a new thread')


@bot.command()
async def status(ctx):
    """Displays current topic and upcoming topics"""
    meeting = meeting_register.get_meeting(ctx.author)
    if not meeting:
        raise ValueError("User not in a meeting")

    embed = discord.Embed()
    for thread in meeting.threads:
        embed.add_field(
            name=thread.name,
            value=f"{thread.initiator.name}#{thread.initiator.discriminator}"
        )

    await ctx.send(embed=embed)


@status.error
@thread.error
async def error_handler(ctx, error):
    if isinstance(error, ValueError):
        await ctx.send("You are not a participant of any meeting.")
        return

    await ctx.send("An unknown error occurred...")


bot.run(TOKEN)