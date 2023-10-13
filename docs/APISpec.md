# API Specification
## Add Song - `/song/add/` (POST)

Add song to the song library. Each song should be a unique version.

**Request**:

```json
[
    {
        "name": "string",
        "album": "string",
        "artist": "string",
        "link": "string", /* Valid Url */
    }
]
```

**Response**:

```json
[
    {
        "song_id": "integer",
        "authorization_key": "string" /* Store this to modify the song later */
    }
]
```
## Delete Song - `/song/{song_id}/remove` (POST)

Remove song from the song library.

**Request**:

```json
[
    {
        "authorization_key": "string" /* Generated at song creation */
    }
]
```

**Response**:

```json
{
    "success": "boolean"
}
```
## Play Song - `/song/{song_id}/play` (GET)

Returns a URL to play the given song corespronging to the song_id

**Returns**:

```json
{
    "url": "string" /* Url in User’s preferred Streaming platform */
}
``` 

## Create User - `/users/create` (POST)

Creates a new user and returns their identifier. The client should send this in a header with every succeeding request.

**Return**:

```json
{
  "user_id": "integer"
}
```


## Set Prefered Platform - `/users/platform` (POST)

Sets the user’s preferred streaming platform. Requires USER_ID Header to be set.

**Request**:

```json
{
    "platform": "string" /* Streaming platform of choice (Spotify, Apple, etc.) */
}
```

**Returns**:

```json
{
    "success": "boolean"
}
```

## Permanently Delete User - `/users/delete/{user_id}` (POST)

Permanently deletes users. Under GDPR and CCPA regulations, this allows the user to withdraw their consent for us to store their data.

**Returns**:

```json
{
    "success":"boolean"
}
```

## Create Playlist - `/playlist/create` (POST)

Create a new playlist

**Request**:

```json
[
  {
    "playlist_name": "string",
  }
]
```
**Return**:

```json
[
  {
    "playlist_id": "int",
  }
]
```

## Add Songs to Playlist - `/playlist/{playlist_id}/songs/add` (POST)

Adds a song to the end of the playlist.

**Request**:

```json
[
  {
    "song_id": "int"
  }
]
```


## Play Playlist - `/playlist/{playlist_id}/play` (GET)

Play the next song in the specified playlist, or if no session, the first song.

**Returns**:

```json
[
    {
       "url": "string" /* Url in User’s preferred Streaming platform */
    }
]
```