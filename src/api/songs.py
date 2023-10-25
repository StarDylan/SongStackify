from typing import Annotated
from fastapi import APIRouter, Header
from pydantic import BaseModel

from src.api.models import SongPlayLink

router = APIRouter(
    prefix="/song",
    tags=["song"],
)

class AddSong(BaseModel):
    name: str
    album: str
    artist: str
    link: str

class AddSongResponse(BaseModel):
    song_id: int
    authorization_key: str

@router.post("/add")
def add_song(add_song: AddSong) -> AddSongResponse:
    """ """
    raise NotImplementedError()


class SongAuthorization(BaseModel):
    authorization_key: str

@router.post("/{song_id}/remove")
def remove_song(song_id: int, authorization: SongAuthorization):
    """ """
    raise NotImplementedError()


@router.get("/{song_id}/play")
def play_song(song_id: int, user_id: Annotated[str | None, Header()]) -> SongPlayLink:
    """ """
    raise NotImplementedError()

