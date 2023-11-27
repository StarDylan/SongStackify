from fastapi import APIRouter, Header
from pydantic import BaseModel
import sqlalchemy
from src import database as db
import json
import requests
import os
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

@router.get("/get_library/")
def get_library(offset: int):
    """
    Gives songs in library by 5 at a time by user offset. 
    If offset is greater than song amount, then no songs will be returned
    """
    library = []

    if offset < 0:
        return "Invalid offset"

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
        # TODO error handle
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
            return "Link Invalid"
        
        return AddSongResponse(authorization_key=result.authorization_key, song_id=result.id)
    

class AddSongLink(BaseModel):
    song_id: int
    link: str


@router.post("/link/add")
def add_link(add_song: AddSongLink):
    """ """
    with db.engine.begin() as connection:
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
            return "Platform link is not supported"
    

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

    result = conn.execute(sqlalchemy.text("""
            SELECT COUNT(*) FROM song_history
            WHERE user_id = :user_id
            """),
            [{
                "user_id": user_id
            }]).scalar_one()
    
    if result < 5:
        return None
    
    result = conn.execute(sqlalchemy.text("""
            SELECT song_name, artist
            FROM song_history
            JOIN songs ON song_history.song_id = songs.id
            WHERE user_id = 23
            ORDER BY song_history.created_at DESC
            LIMIT 5
            """)).all()
    
    song_prompt = "Songs:\n"
    for song in result:
        song_prompt += song.song_name + " by " + song.artist + "\n"

    payload = json.dumps({
        "model": "llama2-uncensored",
        "system": "Classify the user's mood based on the following song titles into only one of these emotions: Happy, Sad, Angry. Only include the classification as one word.",
        "prompt": song_prompt,
        "stream": False
        })
    headers = {
    'Content-Type': 'application/json'
    }

    print("Getting Sentiment from OLLAMA")

    response = requests.request("POST", os.environ.get("OLLAMA_URI"), headers=headers, data=payload)
    response = response.json()
    print(response)

    mood = ""
    if "happy" in response["response"].lower():
        mood = "HAPPY"
    elif "sad" in response["response"].lower():
        mood = "SAD"
    elif "angry" in response["response"].lower():
        mood = "ANGRY"

    if mood == "":
        return None
    
    result = conn.execute(sqlalchemy.text("""
            SELECT link FROM ad_campaigns
            WHERE target_mood = :mood
            ORDER BY RANDOM() """), [{
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
                return SongResponse(url="Invalid user ID", is_ad=False)

            query = conn.execute(sqlalchemy.text("""
                SELECT * FROM songs
                WHERE songs.id = :song_id
                """),
                [{
                    "song_id": song_id
                }]).one_or_none()
                                                 
            if query is None:
                return SongResponse(url="Invalid song ID", is_ad=False)

            return SongResponse(url="Song not available on user's platform", is_ad=False)
        
        ad_link = play_ad_if_needed(conn, user_id)
        if ad_link is not None:
            return SongResponse(url=ad_link, is_ad=True)
        
        conn.execute(sqlalchemy.text("""
          INSERT INTO song_history (user_id, song_id) VALUES (:user_id, :song_id)
            """),
            [{
                "song_id": song_id,
                "user_id": user_id
            }])
        
        return SongResponse(url=query.song_url, is_ad=False)


