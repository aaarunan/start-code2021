# bot.py
import os

from discord.ext import commands
from dotenv import load_dotenv

from meeting import Meeting
from thread import Thread
from meeting_register import MeetingRegister
from exceptions import UserNotInMeetingError

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")
meeting_register = MeetingRegister()


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command()
async def start(ctx: commands.Context, *, args):
    """Starts a meeting or thread"""
    # Check if user is a participant in any meetings
    meeting: Meeting = meeting_register.get_meeting(ctx.author)
    if args[0] == "thread":
        thread_name = " ".join(args[1:])

        # if user is in a meeting
        if meeting is not None:
            meeting.add_thread(thread_name, ctx.author)
        else:
            ctx.send(
                "Thread can not be started because you are not currently in a meeting.."
            )

    meeting_register.addThread(str(ctx.author))
    await ctx.send(str(ctx.author) + " added a new thread")


@bot.command()
async def status(ctx):
    """Displays current topic and upcoming topics"""
    meeting = meeting_register.get_meeting(ctx.author)
    if not meeting:
        raise UserNotInMeetingError("User not in a meeting")

    embed = discord.Embed()
    for thread in meeting.threads:
        embed.add_field(
            name=thread.name,
            value=f"{thread.initiator.name}#{thread.initiator.discriminator}",
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
