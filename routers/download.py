from typing import List, Optional
from pathlib import Path
import requests
import json
from pydantic import AnyHttpUrl
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, UploadFile, Form
from instagrapi.types import (
    Story, StoryHashtag, StoryLink,
    StoryLocation, StoryMention, StorySticker,
    Media, Usertag, Location
)

from dependencies import ClientStorage, get_clients


router = APIRouter(
    prefix="/download",
    tags=["download"],
    responses={404: {"description": "Not found"}},
)




@router.post("/by_url")
async def video_download_by_url(sessionid: str = Form(...),
                         url: str = Form(...),
                         folder: Optional[Path] = Form(""),
                         returnFile: Optional[bool] = Form(True),
                         clients: ClientStorage = Depends(get_clients)):
    """Download video using URL
    """

    cl = clients.get(sessionid)
    media_pk = cl.media_pk_from_url(url)
    media_info = cl.media_info(media_pk)
    media_type = media_info.media_type
    if media_type == 1: # Images
        result = cl.photo_download(media_pk, folder)
    elif media_type == 2:  # Video
        result = cl.video_download(media_pk, folder)
    elif media_type == 8:  # Album
        result = [
            cl.photo_download(item.pk, folder) if item.media_type == 1 else cl.video_download(item.pk, folder)
            for item in media_info.resources
        ]
    elif media_type == 17:  # IGTV
        result = cl.video_download(media_pk, folder)
    if returnFile:
        return FileResponse(result)
    else:
        return result



