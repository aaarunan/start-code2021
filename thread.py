import discord

class Thread:
    """A thread is a new topic within a conversation"""
    def __init__(self, name: str, initiator: discord.User):
        self.name = name
        self.initiator = initiator
        self.queue: [discord.User] = [initiator]

    def __repr__(self) -> str:
        return f"Thread(name={self.name}, initiator={self.initiator})"
    
    def add_comment(self, name: str, user: discord.User) -> None:
        """Adds a comment to a given topic"""
        self.queue.append(user)
        
    def remove_comment(self, user: discord.User) -> None:
        """Removes a comment given by an user name"""
        for i, queue_user in enumerate(self.queue):
            if queue_user == user:
                self.queue.pop(i)
                return    

        raise ValueError("User not found in thread...")

    def remove_current(self) -> None:
        """
        Removes current speaker from queue.
        If the queue is empty, this function does nothing.
        """
        if len(self.queue) != 0:
            self.queue.pop(0) 
                
        