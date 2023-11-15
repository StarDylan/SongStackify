from fastapi import APIRouter
from pydantic import BaseModel
import sqlalchemy
from src import database as db
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes

def hashPassword(password, salt=''):
    h = SHA256.new()
    h.update(bytes(password + salt, "utf-8"))
    hashed = h.hexdigest()
    return hashed    

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class UserIdResponse(BaseModel):
    user_id: int

@router.post("/create")
def create_user(password: str) -> UserIdResponse:
    """ """
    salt = get_random_bytes(4)
    salt_str = salt.hex()
    hashed = hashPassword(password, salt_str)
    with db.engine.begin() as connection:
        user_result = connection.execute(sqlalchemy.text("INSERT INTO users(password, salt)\
                                           VALUES (:password, :salt)\
                                           RETURNING id"),
                                           [{
                                               "password":hashed,
                                               "salt":salt_str
                                           }]).one()
    return user_result.id

@router.post("/platform")
def set_platform(user_id: int, password: str, platform: str):
    """ """
    with db.engine.begin() as connection:
        salt_rsp = connection.execute(sqlalchemy.text(
            """
            SELECT salt
            FROM users
            WHERE id = :user_id
            """
        ),
        [{
            "user_id":user_id
        }]
        ).scalar_one()
        hashed = hashPassword(password, salt_rsp)

        connection.execute(sqlalchemy.text("""UPDATE users
        SET platform_id = sq.sel_platform
        FROM
        (SELECT id as sel_platform
            FROM platforms
            WHERE platform_name=:platform) as sq
        WHERE id=:user_id AND password=:password"""),
        [{
            "user_id":user_id,
            "password":hashed,
            "platform":platform
        }])
    
@router.post("/delete/{user_id}")
def delete_user(user_id: int, password: str):
    """ """
    with db.engine.begin() as connection:
        salt_rsp = connection.execute(sqlalchemy.text(
            """
            SELECT salt
            FROM users
            WHERE id = :user_id
            """
        ),
        [{
            "user_id":user_id
        }]
        ).scalar_one()
        hashed = hashPassword(password, salt_rsp)

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
