class DMs:
    def __init__(self):
        pass

    async def genResponse(self, message):
        if message == "hello":
            return "hi!"
        return "Sorry, I don't know that"
