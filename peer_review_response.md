What we did:
Added Error handling to delete user and set_platform and play_playlist
Remove Platform object from set_platform()
Fixed ER Diagram
Migrated to Argon2id
Added return to add song to playlist
Added route to create a new link for an existing song
Fixed body in API Spec for set platform.
added error handling for invalid URL patterns.
Moved passwords from URL to JSON

#### Other
Add platform doesn’t exist in set platform
Correct, a user cannot add a platform. This must be inputted by the maintainers.

### Robin (Code)
For the add_song_to_playlist method, it would be convenient for the users (leading to a better user experience) to be able to add multiple songs at once into a playlist instead of being able to add only one at a time.
To implement this, I would suggest using some sort of loop and a data structure (maybe a list) to be able to add multiple songs at once into a playlist.
This would be handled by the frontend.



I am not sure if the CreatePlaylist, PlaylistIdResponse, and Song classes are necessary because they only have one attribute that is associated with them.
I would remove these all together, and instead of passing in new_playlist: CreatePlaylist for the create_playlist method (for example), you can just pass in playlist_name: str. This logic would apply for the other classes you remove as well.
This is just to tell Pydantic to set them as body. And the Song class is shared among many routes.

I suggest that it might be better if users are allowed to remove playlists just like they can remove songs. This would enhance the overall user experience because users will not have to go through the burden of having to remove every song from the playlist just to delete the playlist.
We agree, but for right now each playlist should be almost immutable, since many other people might be listening to that playlist and SongStackify is an open and public platform.
For the play_playlist method, there are many things going on and it seems confusing.
I suggest breaking it down into smaller specific methods for better readability and debugging purposes.  
Although the play_playlist is pretty dense, it is all tightly integrated and is hard to separate. 

I would consider more edge cases such as when the playlist_id: int is invalid when adding a song to a playlist for your future implementation.
Fixed!

For the add_song method, since it takes in link: str as a parameter, it is prone to malicious/invalid links.
Therefore, I suggest incorporating a validation mechanism to verify the link’s legitimacy and confirm its connection to the intended site.
This is done by pattern matching when adding to the db.
I feel like the lower half code of the play_song method is redundant when it comes to error handling for checking if the user/song ID is valid or not. I do believe that it can be condensed.
It is necessary to deduce the error and give the user a detailed explanation.
For the parameters of the remove_song method, don’t you need a playlist_id so that users can choose which specific playlist to remove the song from? Or else from where is the song being removed from?
No, the song is deleted from the platform entirely. It is meant to be used by music studios.
If you haven’t thought about that yet, it would be a good idea to allow users to remove songs from the different playlists they have.
We agree, but for right now each playlist should be almost immutable, since many other people might be listening to that playlist and SongStackify is an open and public platform.
The attributes album: str, artist: str, link: str in the Platform class are never used.
Are you planning to use it in your future implementation? If not, I would just remove it.
Fixed!
There is a MAJOR security concern when I create a user. The password created by the user can be seen in the request URL  https://songstackify.onrender.com/users/create?password=random123
I suggest taking a look again at how you are storing passwords in your create_user method.
Fixed!
I also suggest taking a look at built in libraries online for storing/handling passwords so that your service is more secure.
Yes, we are using argon2id now.
I suggest adding condition statements to handle errors for delete_user method (let’s say when someone inputs the wrong user_id: int or password: str intentionally or just by mistake).
Yep fixed!

### Robin (Schema)

Instead of returning an automatically generated user_id: int when creating a new user, a username input and a username output might be more helpful and easy for the user to remember when creating a new user.
The ‘user’ is what we consider a session and this would be managed by the frontend. We also do not wish to store such personal information.

The artist field in the API Spec is given as a string, but in the ER diagram, it shows the artist as an int.
Fixed!
There are fewer tables (no playlist_songs and users_playlist_position table) in the ER diagram compared to what is shown in the schema.sql file. Is there a reason for this?
Some tables are captured in the relations between the entities, the entities are not explicitly tables themselves.
I see no search capability, so it would be nice to implement it in your future version as it will allow users to conveniently search for songs/playlists.
We agree this would be a good feature and we are adding it.
How would you handle the case when a song is already in the playlist but the user is trying to add it? I don’t see any condition checks to see whether a song is already in the playlist or not.
Yes, that is intended, you can add a song multiple times to the same playlist.
Having a way to view all playlists that are available to view (like the get_catalog method in our potions shop) and listen would be a nice feature for your service.



In the Song table of the ER diagram, it has an attribute isrc_number: int, which doesn’t appear in the songs table of the schema.sql file. What is the isrc_number supposed to do or what does it represent?
It was removed because we didn’t use it. It represents a copyright id for a song.

It might be better to limit users to choose only from approved streaming platforms. This way users cannot type in a random string or carelessly misspell the platform.
Yep this would be handled by the frontend.
There could be an additional field when creating a playlist if you want to add the feature of allowing users to specify whether they want the playlist to be public or private.
The design right now is to have an open and public ecosystem, however private playlists are on the roadmap.
I suggest precisely specifying error responses for various situations, incorporating informative messages alongside suitable HTTP status codes.
Fixed!
There is a discrepancy between the Set Preferred Platform outlined in the API Spec and the actual code implementation in users.py.
Fixed!
The set_platform endpoint is seeking three additional attributes (album: str, artist: str, link: str) that are not documented in the API Spec.
Fixed!
When a delete user action is going to be performed, I suggest implementing various user authentication mechanisms to be sure before proceeding.
We believe password is enough to verify a user’s identity before deletion.

### Josh (Schema)

1. Since Playlists are tied to users, perhaps it can be the other way around where the playlists are connected to the platform. Just so you can listen to all different types of music elsewhere.
They are not tied to users. And we wish to combine different platform songs in the same playlist.

2. Seems like the API spec and the ER diagram is slightly a little off. The Artist is an int compared to a string.
Fixed!

3. In the ER diagram, there is something called the isrc_number, which I'm not sure what it means
ISRC number is an id identifying the song’s copyright. I will remove it from the ER diagram because it is currently not implemented.

4. Playing a specific song or starting the playlist in a certain spot of the playlist.
Playing a specific song is implemented. But starting the playlist in a certain spot, while a good idea, is not the current design of “play and forget”

5. Creating a public and or private playlist in which only or other people can add to it.
The design right now is to have an open and public ecosystem, however private playlists are on the roadmap.

6. Having the ability to reach out to other platforms while checking if its a valid site and can play music.
We are an independent platform and would not like to reach out to various proprietary APIs. 

7. Deleting a user is a serious operation and should not be taken lightly. Having first time generated keys that can be in the database so the user can write them down to delete.
We believe that a password is enough to verify user id before deletion.

8. Having a username when signing up would be great, rather than an unique id
The ‘user’ is what we consider a session and this would be managed by the frontend. We also do not wish to store such personal information.

9. It seems to me that there is no check to see if the song already exists before you add it.
Songs are uniquely identified by their URL, the URL is validated as unique in our database.

10. Are Songs supposed to be unique or is the link going to the song supposed to be unique. What if I added two songs that are the exact same but on two diff platforms?
You can add multiple links to a song with the newly added new link route.

11. There is nothing getting returned when I try to add a song to a playlist
Fixed!

12. Creating a function that views all of the songs in a playlist would be beneficial.





### Josh (Code)

1. **Song Removal in songs.py:**
   - The `remove_song` function in songs.py currently removes a song from the available options but not from playlists that added it before. Consider adding functionality to remove it from playlists as well to maintain consistency.

It does indeed also remove from playlists. The cascade functionality of the db ensures this.

2. **Validating Links in songs.py:**
   - In the `add_song` function, which takes a link as a parameter, it's crucial to implement a validation mechanism to ensure that the link is valid and leads to the intended platform. This can help prevent issues with incorrect or malicious links.

We do with pattern matching.

3. **Removing the 'platform' Column in users.py:**
   - Eliminating the 'platform' column in users.py could align with the product mission. Since certain songs are exclusive to specific platforms, consider handling platform-specific logic elsewhere to enhance simplicity.

We store platforms with each user to ensure we serve the correct platform.

4. **user_playlist_position Purpose:**
   - Clarify the purpose of the `user_playlist_position` table in your database schema. Understanding its role is essential for maintaining and evolving the codebase.

This table is to keep track of each user’s position in the various playlists.

5. **Security Concerns in create_user:**
   - Express concern about security when creating a user, as the password is visible in the request URL. Suggest exploring secure methods like using HTTPS and ensuring sensitive information is not exposed in the URL.

Yes we moved the password away from the URL.

6. **Password Hashing in create_user:**
   - Consider storing passwords as hashes instead of using a salt. This enhances security by protecting user passwords even if the database is compromised.

We do store passwords as hashes (using argon2id). In the past implementation, passwords were hashed with SHA256 and included a salt (which by definition is public). The salt is included in the hash when using argon2id.

7. **Valid User Requirement for Adding Songs:**
   - Clarify whether being a valid user is a prerequisite for adding songs to the playlist. If so, enforce appropriate user validation checks in the code.

It is not a prerequisite.

8. **Handling Playlists on User Deletion:**
   - Discuss the decision to either delete or save playlists associated with a user when they delete their profile. The choice depends on your product's user experience goals.

Playlists are independent of users, therefore we will not delete any playlists created.

9. **Error Handling and 'one_or_none()':**
   - Implement error checking, especially in places where the code may fail. The use of 'one_or_none()' is a good practice, but ensure it's complemented by robust error handling mechanisms.

We added error handling to other places of the code.

10. **Documentation on Playlist Platform Consistency:**
	- Consider adding documentation explaining that if songs in a playlist are from different platforms, there might be skipping or handling based on the primary platform.

Added!
11. **Readable Queries and Testing:**
	- Great readable queries that have the ability to be tested and decoupled.

Thanks!
12. **Positive Outlook:**
	- Overall great code and great vision for the project. This is just the start of the project and I can’t wait til yall get everything set and ready :)
- Thanks!

### Ananya (Schema)
1. Tables: The ER diagram is consistent with the tables shown in the schema.sql file. The ER diagram shows fewer tables than appear in the schema.sql file.
Some tables are captured in the relations between the entities, the entities are not explicitly tables themselves.
2. View: It would be nice to have a way to display/view all the playlists similar to catalog in our potion shop.
Fixed!
3. User Profiles: It could be nice to have a complete user profile - username, image, etc.
The ‘user’ is what we consider a session and this would be managed by the frontend. We also do not wish to store such personal information.
4.  Endpoint Mismatch: There is a mismatch between what is requested for set preferred platform in the API spec vs. the implemented code. The endpoint requests two more attributes that are not listed in the spec.
5. User Authentication: Consider implementing user authentication mechanisms, especially when deleting users are involved.
This is already in place.
6. User_Id Consistency: Specify whether the "user_id" should be included in the request body or as a header for the "Set Preferred Platform" endpoint.
7. Song ID Type: Clarify the data type for the "song_id" field in the "Add Song" and "Play Song" responses. It's mentioned as an integer in one place and a string in another. 
Could not find mentions where song_id is references as string.
8. Validation for URL: Specify the expected format for the "link" field in the "Add Song" endpoint. For example, ensure it is a valid URL.
URLs are already pattern matched, added error handling for invalid URL patterns.
9. Error Handling: Clearly define error responses for different scenarios, and include informative messages along with appropriate HTTP status codes.
Generic, error handlings are in the works
10. User Feedback and Ratings: Allow users to provide feedback on songs and playlists through likes. This would enhance engagement to your platform.
Noted, added to feature backlog.
11. Collaboration: It would be awesome if you implemented a shared playlist feature, I personally love this feature in Spotify so I’d love to see that in your work!
Playlists are collaborative by default!
12. Search: A search option could be cool to see as well! This way users could search for songs to find which playlists they have them in, or search through their playlists to find the one they are looking for.
Noted! It's on our roadmap.

### Ananya (Code)
1. `Playlists.py:` There are more edge cases to be considered here. A couple of them that I picked up on were cases such as an empty playlist or invalid user ID, these might be good to implement in the future.
Fixed!
2.  `Playlists.py`: I would remove the separate classes you have in this file. The song, createPlaylist, and PlaylistIdResponse classes only have one attribute which seems unnecessary. I would either remove these all together or add more information to this classes (detailed in the next bullet point)
These are to inform pydantic to put these into the request body.
3. `Playlists.py`: It could be nice to have a description attribute in the CreatePlaylist button and a public or private feature as well. If the playlist is public, it would appear on the user's account and other people could see that playlist. If it’s private, only the user themselves could see it.
The design right now is to have an open and public ecosystem, however private playlists are on the roadmap.
4.  `Playlists.py`: It could be nice to be able to select multiple songs at a time to input into the playlist rather than one at a time.
This can be done in the frontend. 
5.  `Playlists.py`: Remove unused imports, such as Header from fastapi, if they are not used in the current code.
We are using that import
6. `Songs.py`:  Break down play_playlist into smaller functions. This function is doing a lot right now so it would be good to break it into smaller, more focused functions for better readability and maintainability. This can also help you optimize your SQL queries for better performance.
Although the play_playlist is pretty dense, it is all tightly integrated and is hard to separate. 
7. `Songs.py`: The code makes additional unnecessary queries (e.g., SELECT * FROM users) when handling errors. This can be optimized.
These are necessary to determine the exact error.

8.  `Songs.py`: There is some code duplication in the play_song function, especially in the error-handling logic. It uses the same error-checking pattern repeatedly, this could be condensed. For example, you can have an error_message variable that you set to “Invalid user ID” or “Invalid song ID”, etc. You could then do a check if error_message and then return the error message at the end of this function to optimize.

We do this duplication in order to determine the exact error. And this dramatically improves the user experience.

9.  `Songs.py`: Consider adding a liked song feature. It could be cool for a user to see all the songs they have liked like how you can in Spotify and Apply Music.
We will consider it, but the basic functionality is working as designed.

10.  `Users.py`: the album and artist fields of the Platform class are never used.
Fixed!
11.  `Users.py`: I would add more error handling for delete_user and set_platform for if someone inputs an invalid user_id or an invalid password.
Fixed!

12.  `Users.py`: Consider using a more secure method for passwords. There are built in libraries that would be better to use instead of trying to implement your own hashing function. It would also automatically generate a salt and add other security benefits.
We were not implementing our own hashing function, we use sha256. We are upgrading to argon2.

### Caroline (Schema)
1. In the API spec, the artist field for each song is a string but the ER diagram shows the artist as an int.
Fixed!
2. Having to keep track of an individual authorization key for each additional song added is a lot of information to store. Maybe give each user 1 unique authorization key to edit all of their own songs with.
Since we are a privacy respecting platform, we only want to track the bare minimum and don’t want to track which users created which songs. 

3. The ER diagram shows fewer tables than appear in the `schema.sql` file.
Some tables are captured in the relations between the entities, the entities are not explicitly tables themselves.

4. When permanently deleting a user, you could maybe require an authorization key as well as an additional layer of security.
Passwords should be enough to verify the user’s identity.

5. How are you going to deal with a user requesting a certain song on their preferred platform, Limewire, but no one has added an entry with a Limewire link for that song?
The website should notify the user that we do not have that platform and ask the maintainers to add their preferred platform.

6. It would be cool to have something like `get catalog` for the potion shop, where you can view all the playlists people have made.

7. I think there should be an additional input field when creating a playlist for if you want it to be public or private.
The design right now is to have an open and public ecosystem, however private playlists are on the roadmap.

8. You could maybe have a `username` input when creating a new user. It's easier to remember a username you chose than some user_id integer that was automatically generated.
The ‘user’ is what we consider a session and this would be managed by the frontend. We also do not wish to store such personal information.

9. Maybe add another layer of security to the playlists, like user ID or password. Since playlist IDs are generated procedurally, I can put in any playlist ID below mine and start adding stuff to it.
Yes that is by design, we are a public and open ecosystem right now.

10. It might be easier to use a code (1: Spotify, 2: Apple Music, etc.) or choose from approved streaming platforms. The way it is now, a user can enter a randoms string or misspell the platform they want.
The front end should handle this, showing all the various platforms that are available.

11. The description for `Add Song` says each song should be a unique version. How are you checking for that?
Song urls are unique and differentiate the versions. We also just made the col only accept unique values!

12. If I want to add a song that someone else put in the song library, how would I get its ID? I think there should be a method to look at all the songs available, or search by song name.
Implemented a get_library call!

### Caroline (Code)

1. Instead of having a whole table for user playlist position, you could add a column to the playlists table indicating the position or something.
That wouldn’t support multiple users on the same playlist, which we want to support.

2. In `playlists.py` `create_playlist`, I'm not sure that custom classes like `CreatePlaylist` and `PlaylistIdResponse` that just have 1 field are really necessary. Instead of returning a PlaylistIdResponse with an ID, you can just return the playlist ID directly.  
Actually, we implemented it this way because it is more “proper” and more “pedantic.” It helps clarify the flow of different objects and its values. 

3. In `users.py`, `delete_user` and `set_platform`have no error handling if someone inputs a bad user_id or an incorrect password.
Fixed!

4. In `songs.py` `add_song`, I think someone could insert a malicious link with the word "spotify.com" in it somewhere.
This seems to be correct. We fixed the patterns so they now require https://open.spotify.com to be at the beginning of the url.

5. In `songs.py` `remove_song`, I think you can combine the two queries into one. Have the WHERE clause in the second query include id = :song_id AND authorization_key = authorization.authorization_key.
Although this is a good suggestion, we want to do a SELECT first in order to determine which values we get back are invalid and give back to the client the specific parameter that is invalid. If we combine the two statements, we lose the specificity of the error and our team has decided this is an important aspect of our platform. 

6. In `users.py`, the `album` and `artist` fields of the Platform class are never used.
Fixed!

7. I think in `playlists.py`, it might be a good idea to allow users to delete playlists like they can songs.
Added to backlog, thanks for the suggestion. Does not impede user usability of the platform. 

8. In `songs.py` `add_song`, you could probably condense the two queries into one instead of having two different connection.executes.
We like to keep them separate as they are INSERTing into two different tables. The are also in the same transaction.

9. `playlists.py` `play_playlist` seems unnecessarily complicated. It seems like you could just index through the playlist_songs table by user and playlist ID, and offset each time.
No, because there are more factors we take into account, such as when songs get deleted, if the user is valid, if the song is on the user’s preferred platform, etc. Thus, there are a lot of checks we go through to make sure it works properly with all the edge cases.

10. If play_song is being called in play_playlist, I think it makes more sense to be in the `playlists` file than in `songs`. This removes an import as well.

The play_song is a property of the song, and play_playlist plays individual songs. We do need to keep the play_songs in `songs.py` because it is also a route for playing individual songs.

11. A single round of SHA-256 with salting is not a very secure way of storing passwords, as done in `users.py`.
Valid concern, based on OWASP recommendations, switched to Argon2ID with params (64MiB, 4 Iter, 1 Par)

12. In `users.py` `delete_user`, can you combine the two queries into one using a subquery and the hashed function as a parameter? That way only 1 query has to run.

No, because we want to keep the compute on our server and not the database. In the event we want to switch to a more computationally expensive hash function, we want to run that on the server and keep the database load low.

