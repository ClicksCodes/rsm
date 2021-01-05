from fastapi import FastAPI
from uvicorn import Config, Server
from routes import app as Router

app = FastAPI()
@app.get("/")
def root():
    return "Hello, World!"

app.include_router(Router)

async def _start():
    config = Config(
        app,
        host="0.0.0.0",
        port=2064,
        lifespan="on"  # if this isn't specified, you'll get errors when stopping
    )
    config.setup_event_loop()
    server = Server(config)
    try:
        await server.serve()
    except Exception as e:
        raise RuntimeError("Failed to start server.") from e

def start(loop):
    return loop.create_task(_start())

if __name__ == '__main__':
    import asyncio
    start(asyncio.get_event_loop())
