from fastapi import APIRouter, Header
from pydantic import BaseModel
import sqlalchemy
from src import database as db

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
def play_song(song_id: int, user_id: str = Header(None)) -> SongPlayLink:
    """ """
    with db.engine.begin() as conn:
        query = conn.execute(sqlalchemy.text("""
            SELECT song_url from songs
            JOIN links ON links.song_id = songs.id
            WHERE songs.id = :song_id 
            AND links.platform_id = (
                SELECT platform_id FROM users
                WHERE users.id = :user_id
            )
            """),
            [{
                "song_id": song_id,
                "user_id": user_id
            }]).one_or_none()
        
        if query is None:
            # Figure out what the error is
            query = conn.execute(sqlalchemy.text("""
                SELECT * FROM users
                WHERE users.id = :user_id
                """),
                [{
                    "user_id": user_id
                }]).one_or_none()
            
            if query is None:
                return "Invalid user ID"

            query = conn.execute(sqlalchemy.text("""
                SELECT * FROM songs
                WHERE songs.id = :song_id
                """),
                [{
                    "song_id": song_id
                }]).one_or_none()
                                                 
            if query is None:
                return "Invalid song ID"

            return "Song not available on user's platform"
        
        return query.song_url


