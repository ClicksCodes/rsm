from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from authlib.jose import jwt

from pydantic import BaseModel


class VerifyBody(BaseModel):
    jwt: str


app = APIRouter()


@app.post("/verify")
async def verify(body: VerifyBody):
    # You can get the JWT token below
    token = body.jwt

    key = open("./keys/website-public.pem").read()

    ids = jwt.decode(token, key)  # type: jwt.JWTClaims
    print(ids)
    return HTMLResponse("<html><body>200 OK</body></html>")
