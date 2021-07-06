import random

class DMs:
    def __init__(self):
        pass

    async def genResponse(self, message):
        m = message.lower()
        if message in ["hello", "hi"]:
            return random.choice(["Hi!", "Hello!", "Hi there, {mention}!"])
        else:
            return random.choice([
                "Sorry, I don't know that",
                "I don't know how to respond to that",
                "I'm not sure I understand"
            ])
