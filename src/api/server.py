from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import users, songs, playlists, ad
import json
import logging

description = """
SongStackify - Redefining Music Streaming
"""

app = FastAPI(
    title="SongStackify",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Song Stackify Inc.",
        "email": "support@songstackify.com",
    },
)

app.include_router(users.router)
app.include_router(songs.router)
app.include_router(playlists.router)
app.include_router(ad.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to the Central Coast Cauldrons."}
