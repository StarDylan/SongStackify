from fastapi import APIRouter, Depends
from pydantic import BaseModel
import math

from src.api.models import SongPlayLink

router = APIRouter(
    prefix="/playlist",
    tags=["playlist"],
)

class CreatePlaylist(BaseModel):
    playlist_name: str

class PlaylistIdResponse(BaseModel):
    playlist_id: int

@router.post("/create")
def create_playlist(new_playlist: CreatePlaylist) -> PlaylistIdResponse:
    """ """
    raise NotImplementedError()

class Song(BaseModel):
    song_id: str

@router.post("/{playlist_id}/songs/add")
def add_song_to_playlist(playlist_id: int, song: Song):
    """ """
    raise NotImplementedError()

@router.get("/{playlist_id}/play")
def play_playlist(playlist_id: int) -> SongPlayLink:
    """ """
    raise NotImplementedError()

