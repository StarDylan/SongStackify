from typing import Annotated
from fastapi import APIRouter, Header
from pydantic import BaseModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class UserIdResponse(BaseModel):
    user_id: int

@router.post("/create")
def create_user() -> UserIdResponse:
    """ """
    raise NotImplementedError()

class Platform(BaseModel):
    platform: str
    album: str
    artist: str
    link: str

@router.post("/platform")
def set_platform(song_id: int, platform: Platform, user_id: Annotated[str | None, Header()]):
    """ """
    raise NotImplementedError()

@router.post("/delete/{user_id}")
def delete_user(user_id: int):
    """ """
    raise NotImplementedError()

