# Example Flows

## New User wants to Play Single Song
Rian, a Newgrounds user is tired of not being able to share his indie, underground music with his mainstream friends. Not wanting to be like other listeners, he resists using streaming mainstays like Spotify or Apple Music. While these platforms are undeniably convenient, they fell short when it came to showcasing the soul-stirring beats and under-the-radar tracks that form the core of Rians's music collections. Having searched all across the internet, he stumbles upon SongStackify™, the platform that is redefining music streaming. He wants to create playlists on SongStackify™ so that he can play songs through the service.

 - First, Rian creates a new account by calling POST /users/create, which returns his own personal user ID.

Now equipped with his own User ID, Rian goes about playing an indie song he heard about on X, formerly known as Twitter.
- He can play it by calling GET /song/{song_id}/play. The url is then returned to him so he can listen to his newly discovered indie song.

He shares the Song ID with all of his friends on Threads, an IG app, by Meta (formely known as Facebook).

Rian listens to indie music, if you didn’t know.


## Existing User wants to Make a Playlist, Add Songs, and Play it
Rebecka, a SongStackify™ veteran, wants to create a playlist so she can add all her songs from Youtube and Spotify into one playlist on SongStackify. She is tired of switching back and forth on both platforms when she wants to hear songs exclusively on one or the other. It is currently a rainly, dark day and all she wants to do it play her songs and sleep in peace. First, Rebecka starts by creating a playlist by calling POST/playlist/create and passes in a name for her playlist which she calls “sad :( ” to get a playlist_id of 777. 

As a frequent SongStackify™ user, Rebecka has all the song_ids she wants to add to this playlist already in her mind ready to go. The songs she wants to add are “The Funeral” by Band of Horses from Spotify with a song_id of 294 and “Sad Lofi Songs 2023” by Pain from Youtube with a song_id of 983. 
To add her songs she:
- Starts by calling POST/playlist/777/songs/add and passes in her song_id of 294
- Then she does the same with the second song by calling POST/playlist/777/songs/add and passes in the song_id 983.
- To play her playlist, she calls GET/playlist/777/play in which she gets back the url of the first song, “The Funeral” by Band of Horses. 

She goes into bed and snuggles under the cover while the sounds of rain and sad songs play to set the mood. 



## Song Publisher Releases a Song then Faces Backlash
Raleigh, a music executive, decides to use SongStackify™ to publish his company’s latest song. He is very excited. The song was created by Luna Nova and is called "Echoes of Tomorrow”. The song is in the album The Neon Dreamscape and has a url of music.apple.com/neondreamscape/echoesoftomorrow. In order to add this new song he must:

- Call POST /song/add with the name of Echos of Tomorrow, album of The Deon Dreamscape, artist of Luna Nova and a link of music.apple.com/neondreamscape/echoesoftomorrow. He gets back the song_id to publish on his website and an authorization key to keep secret to make changes.

After publishing, he is overwhelmed by backlash on the platform X, formerly known as Twitter. The community was upset that the song uses futuristic and experimental sound, which undermines traditional music values. He decides he must pull the song. In order to do so, he must:

- Call POST /song/{song_id}/ with the authorization key he received when he created the song and the song id in order to remove the song

With the song removed and the community content, Raleigh decides to move past “Echos of Tomorrow” and get ready for his next song release.
