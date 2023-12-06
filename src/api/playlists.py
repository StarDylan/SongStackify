from fastapi import APIRouter, Header
from pydantic import BaseModel
import sqlalchemy
from src.api.songs import play_song, SongResponse
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
    with (db.engine.execution_options(isolation_level="SERIALIZABLE")).begin() as connection:
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
    song_id: int

@router.post("/{playlist_id}/songs/add")
def add_song_to_playlist(playlist_id: int, song: Song):
    """ """
    with db.engine.begin() as connection:
        try: 
            connection.execute(sqlalchemy.text(
                """INSERT INTO playlist_songs(playlist_id, song_id)
                VALUES (:playlist_id, :song_id)"""),
            [{
                "playlist_id":playlist_id,
                "song_id":song.song_id
            }]
            )
        except Exception:
            return "Song doesn't exist"

    return "Success"

@router.get("/{playlist_id}/play")
def play_playlist(playlist_id: int, user_id: str = Header(None)) -> SongResponse:
    """ Will skip songs not in playlist """

    with db.engine.begin() as conn:

        # Check if user id is valid
        try:
            user_valid = conn.execute(sqlalchemy.text("""SELECT id FROM users WHERE id = :user_id"""),
                [{
                    "user_id":user_id
                }]).scalar_one_or_none()
        except Exception:
            return "Invalid user id"
        
        if not user_valid:
            return "Invalid user id"

        position_valid = conn.execute(sqlalchemy.text("""
            SELECT users_playlist_position.playlist_song_position AS pos
            FROM users_playlist_position
            WHERE user_id = :user_id AND playlist_id = :playlist_id
            """),
            [{
                "playlist_id":playlist_id,
                "user_id":user_id
            }]).one_or_none()
        
        if not position_valid or not position_valid.pos:
            # check if playlist exists
            playlist_exists = conn.execute(sqlalchemy.text("""
                SELECT id FROM playlists WHERE id = :playlist_id
                """),
                [{
                    "playlist_id":playlist_id
                }]).scalar_one_or_none()
            if not playlist_exists:
                return "Invalid playlist id"

            first = conn.execute(sqlalchemy.text("""
                SELECT playlist_songs.id AS pos, playlist_songs.song_id AS current_song_id
                FROM playlist_songs
                WHERE playlist_id = :playlist_id
                ORDER BY playlist_songs.id
                LIMIT 1
                """),
                [{
                    "playlist_id":playlist_id
                }]).one_or_none()
            
            if not first:
                return "No songs in playlist"
            
            if not position_valid:
                # User has no position on playlist 
                conn.execute(sqlalchemy.text("""
                    INSERT INTO users_playlist_position(user_id, playlist_id, playlist_song_position)
                    VALUES (:user_id, :playlist_id, :pos)
                    """),
                    [{
                        "playlist_id":playlist_id,
                        "user_id":user_id,
                        "pos":first.pos
                    }])
            else:
                # Need to reset position
                conn.execute(sqlalchemy.text("""
                    UPDATE users_playlist_position
                    SET playlist_song_position = :pos_id
                    WHERE user_id = :user_id AND playlist_id = :playlist_id
                    """),
                    [{
                        "playlist_id":playlist_id,
                        "user_id":user_id,
                        "pos_id":first.pos
                    }])
                    
            response = play_song(first.current_song_id, user_id=user_id)


            if response.is_ad:
                # Rollback position change
                conn.rollback()
                
            return response
        
        else:


            next_song_info = conn.execute(sqlalchemy.text("""
                -- User has valid position on playlist

                WITH next_songs AS (
                SELECT
                    playlist_songs.playlist_id AS playlist_id,
                    playlist_songs.id AS pos_id, 
                    LEAD(playlist_songs.id, 1) OVER (PARTITION BY playlist_songs.playlist_id ORDER BY playlist_songs.id) AS next_pos_id
                FROM playlist_songs
                )

                SELECT playlist_songs.song_id AS current_song_id, next_songs.next_pos_id AS next_pos_id
                FROM users_playlist_position
                JOIN next_songs ON users_playlist_position.playlist_song_position = next_songs.pos_id
                LEFT JOIN playlist_songs ON playlist_songs.id = next_songs.next_pos_id
                WHERE users_playlist_position.user_id = :user_id AND users_playlist_position.playlist_id = :playlist_id
                """),
                [{
                    "playlist_id":playlist_id,
                    "user_id":user_id
                }]).one()
            
            if not next_song_info.current_song_id:
                # Loop back around
                first = conn.execute(sqlalchemy.text("""
                    SELECT playlist_songs.id AS next_pos_id, playlist_songs.song_id AS current_song_id
                    FROM playlist_songs
                    WHERE playlist_id = :playlist_id
                    ORDER BY playlist_songs.id
                    LIMIT 1
                    """),
                    [{
                        "playlist_id":playlist_id
                    }]).one_or_none()
                next_song_info = first
            
            # Set position
            conn.execute(sqlalchemy.text("""
                UPDATE users_playlist_position
                SET playlist_song_position = :pos_id
                WHERE user_id = :user_id AND playlist_id = :playlist_id
                """),
                [{
                    "playlist_id":playlist_id,
                    "user_id":user_id,
                    "pos_id":next_song_info.next_pos_id
                }])

            response = play_song(next_song_info.current_song_id, user_id=user_id)
            
            if hasattr(response, "is_ad") and response.is_ad:
                # Rollback position change
                conn.rollback()
                
            return response

