from fastapi import APIRouter
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from argon2 import PasswordHasher


ph = PasswordHasher()

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

class PasswordRequest(BaseModel):
    password: str

class UserIdResponse(BaseModel):
    user_id: int

@router.post("/create")
def create_user(pw: PasswordRequest) -> UserIdResponse:
    """ """
    # salt is handled by library
    hashed = ph.hash(pw.password)
    with db.engine.begin() as connection:
        user_result = connection.execute(sqlalchemy.text("INSERT INTO users(password)\
                                           VALUES (:password)\
                                           RETURNING id"),
                                           [{
                                               "password":hashed
                                           }]).one()
    return user_result.id

class Platform(BaseModel):
    platform: str

@router.post("/platform")
def set_platform(user_id: int, password: PasswordRequest, platform: str):
    """ """
    hashed = ph.hash(password.password)

    with db.engine.begin() as connection:
       
        connection.execute(sqlalchemy.text("""
        UPDATE users
        SET platform_id = sq.sel_platform
        FROM
        (SELECT id as sel_platform
            FROM platforms
            WHERE platform_name=:platform) as sq
        WHERE id=:user_id AND password=:password
        """),
        [{
            "user_id":user_id,
            "password":hashed,
            "platform":platform
        }])
    # error platform doesn't exist
    return "OK"
    
@router.post("/delete/{user_id}")
def delete_user(user_id: int, password: PasswordRequest):
    """ """
    hashed = ph.hash(password.password)
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """DELETE
                FROM users
                WHERE id=:user_id AND password=:password
            """),
        [{
            "user_id":user_id,
            "password":hashed
        }]
        )
