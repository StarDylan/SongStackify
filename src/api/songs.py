from fastapi import APIRouter, Header
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from src.api.ollamarunner import q
import random


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


def check_valid_offset(offset: int) -> int:
    if offset < 0:
        return f'{offset} must be postive or 0'
    if offset >= 9_223_372_036_854_775_807:
        return f'{offset} is too large'
    
    return None

@router.get("/get_library/")
def get_library(offset: int = 0):
    """
    Gives songs in library by 5 at a time by user offset. 
    If offset is greater than song amount, then no songs will be returned
    """
    library = []

    offset_validity = check_valid_offset(offset)
    if offset_validity is not None:
        return offset_validity

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
        # No Error handling necessary, duplicate songs are fine
        try: 
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
        except Exception:
            return "Link malformed or is not from a supported platform"
        
        return AddSongResponse(authorization_key=result.authorization_key, song_id=result.id)
    

class AddSongLink(BaseModel):
    song_id: int
    link: str


@router.post("/link/add")
def add_link(add_song: AddSongLink):
    """ """
    with (db.engine.execution_options(isolation_level="SERIALIZABLE")).begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                                        SELECT * FROM songs
                                        WHERE id = :song_id
                                        """),
                                    [{
                                        "song_id": add_song.song_id
                                    }]).one_or_none()
        
        if result is None:
            return "Invalid song ID"
        try:
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
                                            "song_id": add_song.song_id,
                                            "song_url": add_song.link,
                                            "url": add_song.link 
                                        }])
            return "Added Link"
        except Exception:
            return "Link malformed, already exists, or is not from a supported platform"
    

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


def play_ad_if_needed(conn, user_id) -> str | None:
    if random.choice([True, False]):
        return None

    # Check if mood is already cached

    result = conn.execute(sqlalchemy.text("""
        SELECT last_updated, mood, songs_played
        FROM user_moods
        WHERE user_id = :user_id
                                          """
                                            ), [{
            "user_id": user_id
        }]).one_or_none()
    if result is None:
        # no mood calculated
        # mood = gen_mood(conn, user_id)
        print("calling ollama")
        q.put(user_id)
        return None
    elif result.songs_played >= 5:

        print("calling ollama")
        q.put(user_id)
    mood = result.mood
    
    result = conn.execute(sqlalchemy.text("""
            SELECT link FROM ad_campaigns
            WHERE target_mood = :mood
            ORDER BY RANDOM() 
            LIMIT 1
                                          """), [{
                "mood": mood
            }]).scalar_one_or_none()

    if result is None:
        return None
    
    return result

class SongResponse(BaseModel):
    url: str
    is_ad: bool


@router.get("/{song_id}/play")
def play_song(song_id: int, user_id: str = Header(None)) -> SongResponse:
    """ """
    with db.engine.begin() as conn:
        try:
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
        except Exception:
            return "Invalid user ID or song ID"
        
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
        
        ad_link = play_ad_if_needed(conn, user_id)
        if ad_link is not None:
            return SongResponse(url=ad_link, is_ad=True)
        
        conn.execute(sqlalchemy.text("""
          INSERT INTO song_history (user_id, song_id) VALUES (:user_id, :song_id);
          UPDATE user_moods
          SET songs_played = songs_played + 1
          WHERE user_id = :user_id
            """),
            [{
                "song_id": song_id,
                "user_id": user_id
            }])
        
        return SongResponse(url=query.song_url, is_ad=False)

@router.get("/search/{query}")
def search_song(query: str, page: int=0) -> list:
    library = []

    if page > 9_223_372_036_854_775_807:
        return "Page is too large"
    if page < 0:
        return "Page must be positive or 0"
    
    with db.engine.begin() as conn:
        library_result = conn.execute(sqlalchemy.text("""
            SELECT id, song_name, artist, album
            FROM songs
            WHERE 
                song_name like :query
            OR artist like :query
            LIMIT 10
            OFFSET :offset
                                             """),
            [{
                "query":query + "%",
                "offset":page*10
            }])
    for song in library_result:
        library.append(
            {
                "Song_Id": song.id,
                "Song_Name": song.song_name,
                "Artist": song.artist,
                "Album": song.album
            }
        )
    if len(library) < 10:
        library = []
        with db.engine.begin() as conn:
            library_result = conn.execute(sqlalchemy.text("""
                SELECT id, song_name, artist, album
                FROM songs
                WHERE 
                    song_name like :query
                    OR artist like :query
                LIMIT 10
                OFFSET :offset
                                                """),
                [{
                    "query": "%" + query + "%",
                    "offset": page*10
                }])
        
        for song in library_result:
            library.append(
                {
                    "Song_Id": song.id,
                    "Song_Name": song.song_name,
                    "Artist": song.artist,
                    "Album": song.album
                }
            )
    return library