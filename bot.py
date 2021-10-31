# bot.py
import os
from typing import List

from dotenv import load_dotenv
import discord
from discord.ext import commands

from meeting import Meeting
from meeting_register import MeetingRegister
from utils import mute_all, unmute_all

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="!", intents=intents)
meeting_register = MeetingRegister()


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command()
async def create(ctx: commands.Context, *args):
    """Starts a meeting or thread"""
    # Check if user is a participant in any meetings
    meeting: Meeting = meeting_register.get_meeting_from_user(ctx.author)
    if args[0] == "thread":
        if len(args) == 1:
            await ctx.send("You must specify a thread name")
            return
        thread_name = " ".join(args[1:])

        # if user is in a meeting
        if meeting is not None:
            meeting.add_thread(thread_name, ctx.author)
            await ctx.send(f"{ctx.author} added a new thread")
        else:
            await ctx.send(
                "Thread can not be started because you are not currently in a meeting.."
            )
            return

        if len(meeting.threads) == 1 and len(meeting.threads[0].queue) == 1:
            await mute_all(meeting)
            await meeting.current_speaker.edit(mute=False)

    if args[0] == "meeting":
        if meeting is None:
            try:
                channel = ctx.author.voice.channel
                meeting_register.create_meeting(channel)
                meeting: Meeting = meeting_register.get_meeting_from_voice_channel(channel)
                await unmute_all(meeting)
                await ctx.send(f"{ctx.author} started a new meeting")
            except AttributeError:
                # Author is not in voicechannel
                await ctx.send("You must be in a voice channel to start a meeting.")
        else:
            await ctx.send(
                "You cannot start a new meeting while you are currently in a meeting."
            )
        
    if args[0] == "comment":
        thread_name = " ".join(args[1:])
        thread = meeting.get_thread(thread_name)
        if thread is not None:
            if ctx.author not in thread.queue:
                thread.add_comment(ctx.author)
                await ctx.send(f"{ctx.author} added a comment to '{thread_name}'")
            else:
                await ctx.send(f"{ctx.author} is currently in the thread '{thread_name}'")
        else:
            await ctx.send(f"No thread is named '{thread_name}")
        



@bot.command()
async def end(ctx: commands.Context, *args) -> None:
    """Ends a meeting"""
    meeting = meeting_register.get_meeting_from_user(ctx.author)
    if args[0] == "meeting":
        if meeting is not None:
            await unmute_all(meeting)
            await meeting_register.end_meeting(ctx.author.voice.channel)
            
        else:
            await ctx.send(
                "There does not seem to be a meeting to end (you are not in an active meeting)"
            )


@bot.command()
async def status(ctx):
    """Displays current topic and upcoming topics"""
    
    meeting = meeting_register.get_meeting_from_user(ctx.author)

    if not meeting:
        embed = discord.Embed(description="You are not a participant of any meeting.")
    elif len(meeting.threads) == 0:
        embed = discord.Embed(description="There are no threads in the current meeting.")
    else:
        embed = discord.Embed(description="Here are the threads for the current meeting you are in:")
        for i, thread in enumerate(meeting.threads):
            field_value = "\n".join(["- " + str(u) for u in thread.queue[1:]])

            embed.add_field(
                name=f"{thread.name} (author: {thread.initiator})",
                value=f"Queue:\n*- {thread.queue[0]}{' (current speaker)*' if i == 0 else ''}\n{field_value}",
                inline=False
            )

    await ctx.send(embed=embed)


@bot.event
async def on_voice_state_update(
    member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
):
    old_voice_channel: discord.VoiceChannel = before.channel
    new_voice_channel: discord.VoiceChannel = after.channel
    old_meeting = meeting_register.get_meeting_from_voice_channel(old_voice_channel)
    new_meeting = meeting_register.get_meeting_from_voice_channel(new_voice_channel)

    # Meeting is either None (if user is not inn a meeting) or a Meeting instance.
    if old_voice_channel != new_voice_channel:
        if old_meeting is not None:
            old_meeting.remove_participant(member)
        if new_meeting is not None:
            new_meeting.add_participant(member)

        if not member.voice.mute:
            await member.edit(mute=True)
            await old_meeting.current_speaker.edit(mute=True)
            old_meeting.next_speaker()
            if old_meeting.current_speaker != None:
                await old_meeting.current_speaker.edit(mute=False)
        else:
            if new_meeting is None:
                await member.edit(mute=False)
        return

    # Changed from unmuted to muted
    # The speaker has stopped speaking and the next person can now speak
    if not before.self_mute and after.self_mute:
        await old_meeting.current_speaker.edit(mute=True)
        old_meeting.next_speaker()
        if old_meeting.current_speaker != None:
            await old_meeting.current_speaker.edit(mute=False)
        else:
            await unmute_all(old_meeting)
            


@status.error
async def error_handler(ctx, error):
    await ctx.send(f"An unknown error occurred...\n```{error}```")


bot.run(TOKEN)
