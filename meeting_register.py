from typing import List, Union

from discord.ext import commands
from meeting import Meeting
from exceptions import MeetingNotFoundError

import discord


class MeetingRegister:
    def __init__(self):
        self.meetings: List[Meeting] = []

    def create_meeting(self, channel: discord.VoiceChannel) -> None:
        """Creates a meeting and adds the meeting to the list of meetings"""
        meeting = Meeting(channel)
        self.meetings.append(meeting)

    def get_meeting_from_user(self, user: discord.User) -> Union(Meeting, None):
        """Returns a meeting the user is a participant of"""
        for meeting in self.meetings:
            if user.id in map(lambda participant: participant.id, meeting.participants):
                return meeting
        return None

    def remove_meeting(self, meeting_name: str) -> None:
        """Removes meeting from the meeting_register"""
        for i, meeting in enumerate(self.meetings):
            if meeting.name == meeting_name:
                self.meetings.pop(i)
                return
        raise MeetingNotFoundError("Meeting not found...")

    def remove_user_from_meetings(self, user: discord.User) -> None:
        """
        Removes user from all meeting where they are a participant,
        and from all threads they are queued in.
        """
        for meeting in self.meetings:
            if user in meeting.participants:
                meeting.remove_participant(user)

            if len(meeting.participants) == 0:
                self.remove_meeting(meeting)
                meeting.end()
                continue

            for thread in meeting.threads:
                thread.remove_comment(user)
