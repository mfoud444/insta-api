from multiprocessing import Process, Queue
import pkg_resources
import logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse, JSONResponse
from routers import (
    auth, media, video, photo, user,
    igtv, clip, album, story,
    insights
)
from bot import TelegramBot 
import nest_asyncio
import asyncio
import uvicorn

app = FastAPI()
app.include_router(auth.router)
app.include_router(media.router)
app.include_router(video.router)
app.include_router(photo.router)
app.include_router(user.router)
app.include_router(igtv.router)
app.include_router(clip.router)
app.include_router(album.router)
app.include_router(story.router)
app.include_router(insights.router)

@app.get("/", tags=["system"], summary="Redirect to /docs")
async def root():
    """Redirect to /docs"""
    return RedirectResponse(url="/docs")

@app.get("/version", tags=["system"], summary="Get dependency versions")
async def version():
    """Get dependency versions"""
    versions = {}
    for name in ('instagrapi', ):
        item = pkg_resources.require(name)
        if item:
            versions[name] = item[0].version
    return versions

@app.exception_handler(Exception)
async def handle_exception(request, exc: Exception):
    return JSONResponse({
        "detail": str(exc),
        "exc_type": str(type(exc).__name__)
    }, status_code=500)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="instagrapi-rest",
        version="1.0.0",
        description="RESTful API Service for instagrapi",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

class MainApp:
    def __init__(self):
        self.bot = TelegramBot()

    def run(self):
        # Run the Telegram bot in a separate process
        bot_process = Process(target=self.bot.run)
        bot_process.start()

        # Run the FastAPI app
        uvicorn.run(app, host="0.0.0.0", port=8000)

        # Wait for the bot process to finish
        bot_process.join()

if __name__ == '__main__':
    nest_asyncio.apply()
    logging.basicConfig(level=logging.INFO)
    main_app = MainApp()
    main_app.run()