## User Stories

1. As a Apple Music user, I want to be able to listen to playlists built on other platforms, so that I can share music with friends who use other platforms
2. As a normal listener, I want to be able to pause, play, and skip songs on demand, so that I can have control over what I listen to.
3. As a celebrity, I want to publicly share my playlists with my fans so that they can further their parasocial relationship by listening to what I listen to.
4. As a normal listener, I want to be able to add songs to already existing playlists so that my playlist can grow with the same themes I set.
5. As a normal listener, I want to be able to delete songs from my playlist so that when I get tired of a song, I don’t need to listen to them anymore. 
6. As a private individual, I want to create private playlists, so that no one can find out what I’m listening to.
7. As a travel enthusiast, I want to listen where I left off even when I change devices or time zones, so that I don’t need to listen to the beginning of the current song or my playlist again.
8. As a national record label representative, I want to customize the naming and cover image, so that we can share our latest albums / playlists with the world with our unique brand.
9. As a record label lawyer, I want to be able to get the ISRC number for any song hosted on this platform, so that I can sue anyone who uploads a bootleg copy of a song.
10. As an indecisive listener, I want to be able to add songs on-the-fly to my queue as I’m listening without altering my playlist, so that I can listen to the song I want to at the moment.
11. As a normal listener, I want to be able to reorder the songs in my playlist so that I can listen to a set lineup of songs in the order I please. 
12. As a picky listener, I want to be able to make my own “forks” of other people’s playlist, so that I can customize it to my liking.
13. As a listener with friends, I want to be able to make collaborative playlists, so that we can build playlists to listen to together.

## Exceptions

1. Exception: The song the user was listening to was deleted.

    On resume of the music, the player will error and notify the user that the song was deleted.


2. Exception: Unauthorized user tries to access private playlist

    If an unauthorized user tries to access someone else’s private playlist, the player will give an error and redirect the user back to their own list of playlists.

3. Exception:  Share Playlist with a Non-Existent User

	If a user tries to share their playlist with a non-existent user, the player will give an 	error message and ask to double check the username.

4. Exception: A user attempts to skip forwards or backwards at the end or beginning of a playlist, respectively.

    If a user skips “off the playlist” the next song played will loop around to the beginning or end the the playlist

5. Exception: A user tries to create a playlist without the required information (title, artist, album, at least one link)
	
    The user will be shown an error and be prompted to supply the missing    information

6. Exception: A user tries to play a song using their preferred streaming service, but a link to the service is not available

    The user will be prompted to provide the link for the given song on their preferred streaming service and will have the option to mark the song as unavailable

7. Exception: Tries to reuse a deleted User ID
    
    The service will notify that the user id they specified doesn’t exist and prompts them to create a new user id.

8. Exception: User tries to submit an invalid link (doesn’t start with https://<streaming_service.com>)

    Notify the user that the URL format is incorrect and suggest the intended format the URL must be in.

9. Exception: A user attempts to access an ISRC number that is Null

    The user will be prompted to fill in the missing ISRC number.
	
10. Exception: User tries to delete a Song from an Empty Playlist

    If the user tries to delete a song from an empty playlist, the player will respond with an error message and say that there is no song to delete as the playlist is empty.

11. Exception: User tries to create a Song Title that is too long

	The user will be prompted that the song title is too long and they must shorten it to 	the maximum length and fail the create song operation.

12. Exception: User uploads an image that is too big

    The user will be prompted to use another image that is below the max image size and the image will not be set.