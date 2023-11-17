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

@router.get("/get_library/", tags=["library"])
def get_library(offset: int):
    """
    Gives songs in library by 5 at a time by user offset. 
    If offset is greater than song amount, then no songs will be returned
    """
    library = []

    get_songs = """
                SELECT id, song_name, artist, album
                FROM songs
                LIMIT 5
                OFFSET :offset;
                """
    
    with db.engine.begin() as connection:
        library_result =  connection.execute(sqlalchemy.text(get_songs),
                                             [{"offset": offset}]).all()
        
        for song in library_result:
            library.append(
                {
                    "Song_Id": song.id,
                    "Song_Name": song.song_name,
                    "Artist": song.artist,
                    "Album": song.album
                }

            )
            
    print(library)

    return library

@router.post("/add")
def add_song(add_song: AddSong) -> AddSongResponse:
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                        INSERT INTO songs (song_name, album, artist)
                                        VALUES (:name, :album, :artist)
                                        RETURNING authorization_key, id
                                        """),
                                    [{
                                        "name": add_song.name,
                                        "album": add_song.album,
                                        "artist": add_song.artist
                                    }]).one()
        connection.execute(sqlalchemy.text("""
                                        INSERT INTO links (song_id,song_url, platform_id)
                                        VALUES (:song_id, :song_url,
                                            (
                                            SELECT platforms.id
                                            FROM platforms
                                            WHERE :url LIKE platforms.platform_url
                                            ))
                                        """),
                                    [{
                                        "song_id": result.id,
                                        "song_url": add_song.link,
                                        "url": add_song.link 
                                    }])
        
        return AddSongResponse(authorization_key=result.authorization_key, song_id=result.id)
    


class SongAuthorization(BaseModel):
    authorization_key: str

@router.post("/{song_id}/remove")
def remove_song(song_id: int, authorization: SongAuthorization):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                        SELECT authorization_key
                                        FROM songs
                                        WHERE id = :song_id
                                        """),
                                    [{
                                        "song_id": song_id
                                    }]).scalar_one_or_none()
        
        if result is None:
            return "Invalid song ID"
        
        if result != authorization.authorization_key:
            return "Invalid authorization key"
        
        result = connection.execute(sqlalchemy.text("""
                                        DELETE FROM songs
                                        WHERE id = :song_id
                                        """),
                                    [{
                                        "song_id": song_id
                                    }])
    
    return "Song Removed"


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


