from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from pydantic import BaseModel


class VerifyBody(BaseModel):
    jwt: str


app = APIRouter()


@app.post("/verify")
async def verify(body: VerifyBody):
    # You can get the JWT token below
    jwt = body.jwt

    # do whatever processing you need here

    # Return an empty(ish) HTML response
    return HTMLResponse("<html><body>200 OK</body></html>")
