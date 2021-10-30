# bot.py
from _typeshed import NoneType
import os
from typing import List

from dotenv import load_dotenv
import discord
from discord.ext import commands

from meeting import Meeting
from meeting_register import MeetingRegister

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")
meeting_register = MeetingRegister()


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command()
async def create(ctx: commands.Context, *, args: List[str]):
    """Starts a meeting or thread"""
    # Check if user is a participant in any meetings
    meeting: Meeting = meeting_register.get_meeting(ctx.author)
    if args[0] == "thread":
        thread_name = " ".join(args[1:])

        # if user is in a meeting
        if meeting is not None:
            meeting.add_thread(thread_name, ctx.author)
            await ctx.send(f"{ctx.author} added a new thread")
        else:
            await ctx.send(
                "Thread can not be started because you are not currently in a meeting.."
            )

        if len(meeting.threads) == 1 and len(meeting.threads[0].queue) == 1:
            meeting.current_speaker.add_roles(
                discord.utils.get(ctx.guild.roles, name="Speaker")
            )

    if args[0] == "meeting":
        if meeting is None:
            try:
                channel = ctx.message.author.voice.voice_channel
                meeting_register.create_meeting(channel)
                await ctx.send(f"{ctx.author} started a new meeting")
            except AttributeError:
                # Author is not in voicechannel
                await ctx.send("You must be in a voice channel to start a meeting.")
        else:
            await ctx.send(
                "You cannot start a new meeting while you are currently in a meeting."
            )


@bot.command()
async def end(ctx: commands.Context, *, args: List[str]) -> None:
    """Ends a meeting"""

    meeting = meeting_register.get_meeting_from_author(ctx.author)
    if args[0] == "meeting":
        if meeting is not None:
            meeting_register.end_meeting(ctx.author.voice.voice_channel)
        else:
            ctx.send(
                "There does not seem to be a meeting to end (you are not in an active meeting)"
            )


@bot.command()
async def status(ctx):
    """Displays current topic and upcoming topics"""
    meeting = meeting_register.get_meeting_from_author(ctx.author)
    if not meeting:
        await ctx.send("You are not a participant of any meeting.")

    embed = discord.Embed()
    for thread in meeting.threads:
        embed.add_field(
            name=thread.name,
            value=f"Thread author: {thread.initiator.name}#{thread.initiator.discriminator}",
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

    speaker_role = discord.utils.get(member.guild.roles, name="Speaker")

    # Meeting is either None (if user is not inn a meeting) or a Meeting instance.
    if old_voice_channel != new_voice_channel:
        if old_meeting is not None:
            old_meeting.remove_participant(member)
        if new_meeting is not None:
            new_meeting.add_participant(member)

        if speaker_role in member.roles:
            await member.remove_roles(speaker_role)
            old_meeting.next_speaker()
            if old_meeting.current_speaker != None:
                old_meeting.current_speaker.add_roles(speaker_role)
        return

    # Changed from unmuted to muted
    # The speaker has stopped speaking and the speaker role
    # can now be moved to the next speaker in queue
    if not before.self_mute and after.self_mute:
        old_meeting.next_speaker()
        member.remove_roles(speaker_role)
        if old_meeting.current_speaker != None:
            old_meeting.current_speaker.add_roles(speaker_role)


@status.error
async def error_handler(ctx, error):
    await ctx.send("An unknown error occurred...")


bot.run(TOKEN)
