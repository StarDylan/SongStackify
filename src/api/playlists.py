from fastapi import APIRouter, Header
from pydantic import BaseModel
import sqlalchemy
from src.api.models import SongPlayLink
import src.database as db 

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
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                        INSERT INTO playlists (name)
                                        VALUES (:playlist_name)
                                        RETURNING id
                                        """),
                                    [{
                                        "playlist_name": new_playlist.playlist_name
                                    }]).one()
    return PlaylistIdResponse(playlist_id=result.id)

class Song(BaseModel):
    song_id: str

@router.post("/{playlist_id}/songs/add")
def add_song_to_playlist(playlist_id: int, song: Song):
    """ """
    with db.engine.begin() as connection:
        user_result = connection.execute(sqlalchemy.text(
            """INSERT INTO playlist_songs(playlist_id, song_id)
            VALUES (:playlist_id, :song_id)"""),
        [{
            "playlist_id":playlist_id,
            "song_id":song
        }]
        )

@router.get("/{playlist_id}/play")
def play_playlist(playlist_id: int, user_id: str = Header(None)) -> SongPlayLink:
    """ """
    
    raise NotImplementedError()

