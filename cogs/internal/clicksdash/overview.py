from fastapi.responses import JSONResponse
from pydantic import BaseModel
import typing


class Index(BaseModel):
    userID: typing.Optional[int]
    guildID: typing.Optional[int]
    items: typing.List[str] = []


async def overview(bot, request):
    if request.userID is None:
        return JSONResponse({"error": "No user id provided."}, 400)
    if request.guildID is None:
        return JSONResponse({"error": "No guild id provided."}, 400)
    guild = bot.get_guild(int(request.guildID))
    handlers = bot.get_cog("Verification").handlers
    out = {}
    for item in request.items:
        if item == "netMembers":
            out[item] = "Coming Soon"
        if item == "activeMembers":
            out[item] = "Coming Soon"
        if item == "totalMembers":
            out[item] = guild.member_count
        if item == "modActions":
            out[item] = "Coming Soon"
        if item == "verifiedMembers":
            role = handlers.fileManager(request.guildID)["verify_role"]
            if role is None:
                out[item] = "Verification not set up"
            else:
                verifiedRole = guild.get_role(role)
                out[item] = len([1 for m in guild.members if verifiedRole in [r.id for r in m.roles]])
        if item == "netVerifiedMembers":
            out[item] = "Coming Soon"

        if item == "liveLogs":
            out[item] = "Coming Soon"
        if item == "quickActions":
            out[item] = "Coming Soon"
        if item == "tags":
            out[item] = handlers.fileManager(request.guildID)["tags"]

        if item == "modTickets":
            out[item] = "Coming Soon"

        if item == "memberGraph":
            out[item] = "Coming Soon"

    return JSONResponse(out, 200)
