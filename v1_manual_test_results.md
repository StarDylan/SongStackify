# Example workflow
Rian, a Newgrounds user is tired of not being able to share his indie, underground music with his mainstream friends. Not wanting to be like other listeners, he resists using streaming mainstays like Spotify or Apple Music. While these platforms are undeniably convenient, they fell short when it came to showcasing the soul-stirring beats and under-the-radar tracks that form the core of Rians's music collections. Having searched all across the internet, he stumbles upon SongStackify™, the platform that is redefining music streaming. He wants to create playlists on SongStackify™ so that he can play songs through the service.

 - First, Rian creates a new account by calling POST /users/create, which returns his own personal user ID.

Now equipped with his own User ID, Rian goes about playing an indie song he heard about on X, formerly known as Twitter.
- He can play it by calling GET /song/{song_id}/play. The url is then returned to him so he can listen to his newly discovered indie song.

He shares the Song ID with all of his friends on Threads, an IG app, by Meta (formely known as Facebook).

Rian listens to indie music, if you didn’t know.


# Testing results
### Create User

```bash
curl -X 'POST' \
  'http://localhost:8000/users/create' \
  -H 'accept: application/json' \
  -d ''
```

Response:
```
4
```


### Play Song
```bash
curl -X 'GET' \
  'http://localhost:8000/song/1/play' \
  -H 'accept: application/json' \
  -H 'user-id: 4'
```


Response:
```
"https://open.spotify.com/track/003vvx7Niy0yvhvHt4a68B?si=095e444ca83840c7"
```