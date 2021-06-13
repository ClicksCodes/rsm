import json
import discord


with open("./data/emojis.json") as emojis:
    _emojis = json.load(emojis)


class Emojis:
    def __init__(self, emojis=_emojis, progress=None, idOnly=False):
        self.emojis = emojis
        self.progress = progress or []
        self.idOnly = idOnly

    def convert(self, emoji):
        animated = ""
        if isinstance(self.emojis[emoji], str):
            animated = "a"
            emoji = self.emojis[emoji][1:]
        else:
            emoji = self.emojis[emoji]
        if self.idOnly:
            return emoji
        return f"<{animated}:a:{emoji}>"

    def __getattr__(self, item):
        self.progress.append(item)
        try:
            _ = self.emojis[".".join(self.progress)]
            return self.convert(".".join(self.progress))
        except KeyError:
            return self.__class__(self.emojis, self.progress, idOnly=self.idOnly)

    def __call__(self, item):
        try:
            _ = self.emojis[item]
            return self.convert(item)
        except KeyError:
            return KeyError(f"Emoji '{item}' does not exist")

    def __getitem__(self, item):
        try:
            _ = self.emojis[item]
            return self.convert(item)
        except KeyError:
            return KeyError(f"Emoji '{item}' does not exist")

    def __str__(self):
        return self.convert(".".join(self.progress))


class Colours:
    c = '\033[0m'

    RedDark = '\033[31m'
    GreenDark = '\033[32m'
    YellowDark = '\033[33m'
    BlueDark = '\033[34m'
    PinkDark = '\033[35m'
    CyanDark = '\033[36m'

    Red = '\033[91m'
    Green = '\033[92m'
    Yellow = '\033[93m'
    Blue = '\033[94m'
    Pink = '\033[95m'
    Cyan = '\033[96m'


class Cols:
    def __init__(self, emojis=None, progress=None):
        self.cols = {
            "red": 0xF27878,
            "yellow": 0xF2D478,
            "green": 0x68D49E
        }

    def __getattr__(self, item):
        try:
            return self.cols[item]
        except KeyError:
            return AttributeError(f"Emoji '{item}' does not exist")

    def __call__(self, item):
        try:
            return self.cols[item]
        except KeyError:
            return AttributeError(f"Emoji '{item}' does not exist")

    def __getitem__(self, item):
        try:
            return self.cols[item]
        except KeyError:
            return AttributeError(f"Emoji '{item}' does not exist")


loading_embed = discord.Embed(
    title=f"{Emojis().icon.loading} Loading",
    description="Your command is being processed",
    colour=Cols().red
).set_footer(text="If the message does not load in 5 seconds, something is probably broken")
