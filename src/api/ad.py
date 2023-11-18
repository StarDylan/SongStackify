from fastapi import APIRouter
from enum import Enum
import sqlalchemy
import src.database as db 

router = APIRouter(
    prefix="/ad",
    tags=["ad"],
)

class MoodEnum(str, Enum):
    sad = 'SAD'
    happy = 'HAPPY'
    angry = 'ANGRY'


@router.post("/create")
def create_playlist(link: str, mood: MoodEnum):
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
            INSERT INTO ad_campaigns (link, target_mood) VALUES (:link, :mood)
            """),
            [{
                "link": link,
                "mood": mood
            }])
        
    return "Success"