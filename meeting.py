from typing import List, Union

import discord

from exceptions import ThreadNotInMeetingError, UserNotInThreadError
from thread import Thread


class Meeting:
    """A Meeting that holds "threads" which are topics to be discussed"""

    def __init__(self, channel: discord.VoiceChannel):
        self.channel = channel
        self.participants: List[discord.User] = [user for user in channel.members]
        self.threads: List[Thread] = []

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
        if len(self.threads[0].queue) == 0:
            self.threads.pop(0)

    def add_participant(self, user: discord.User) -> None:
        """Adds a participant to a meeting"""
        self.participants.append(user)

    def remove_participant(self, user: discord.User) -> None:
        """Removes a participant to a meeting"""
        try:
            self.participants.remove(user)
        except ValueError as e:
            raise UserNotInThreadError(e)

    @property
    def current_speaker(self) -> Union[discord.User, None]:
        """Gets the current speaker"""
        try:
            return self.threads[0].current_speaker
        except IndexError:
            return None

    async def end(self) -> None:
        """Ends a meeting by notifying participants"""
        for user in self.participants:
            await user.send(f"The meeting in {self.channel} has ended.")
