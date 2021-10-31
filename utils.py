from meeting import Meeting
import discord

async def unmute_all(meeting: Meeting) -> None:
    for member in meeting.participants:
        await member.edit(mute=False)
    
async def mute_all(meeting: Meeting) -> None:
    for member in meeting.participants:
        await member.edit(mute=True)