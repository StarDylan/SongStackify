from pydantic import BaseModel


class SongPlayLink(BaseModel):
    url: str
