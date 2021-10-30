import discord
from discord.ext import commands
from thread import Thread
from exceptions import ThreadNotInMeetingError

class Meeting:
    """A Meeting that holds "threads" which are topics to be discussed"""
    def __init__(self, context: commands.Context, channel: discord.VoiceChannel, initiator: discord.User):
        self.context = context
        self.channel = channel
        self.participants: [discord.User] = []
        self.threads: [Thread] = []

    
    def add_thread(self, thread_name: str, initiator: discord.User) -> None:
        """Adds a thread to the meeting"""
        thread = Thread(thread_name, initiator)
        self.threads.append(thread)
        
    def remove_thread(self, thread_name: str) -> None:
        """Removes a thread with the given name from the current meeting"""
        for i, thread in enumerate(self.threads):
            if thread.name == thread_name:
                self.threads.pop(i)
                return
        raise ThreadNotInMeetingError("Thread not found in meeting...")
        
    def next_speaker(self) -> None:
        """Sets the speaker to the next user in the queue"""
        self.threads[0].remove_current()
        if len(self.threads) == 0:
            self.threads.pop(0)
        
    def end(self) -> None:
        """Ends a meeting by notifying participants"""
        # """?????""" Meldinger burde ikke sendes utenfor main!!:
        await self.context.send("The meeting in " + self.channel + " has ended.")
        
        # self.context | https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#context
        

        
                
        