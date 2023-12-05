## Fake Data Modeling

Fake data was create with [fake_data_generator.py](fake_data_generator.py).

The script is hardcoded to create 3000 playlists, it then uses the defined ratios to generate the users with randomly assigned playlists.

Using real data from Spotify, the script creates all the songs that exist in the playlists, and then creates the links to the platform (some are with Spotify, some are with Apple Music, other are with both).

We assume each user will only play songs from their playlist(s) and will play through the full playlist at least a few times.

Total Counts:
- 3,000 playlists
- 911 users
- 77,803 songs
- 202,899 playlist_songs
- 3,000 playlist_user_positions
- 919,039 song_history
- 85,515 links
- 2 platforms
- 100 ad campaigns

Total of 1,292,269 rows in the database.

We think this distribution is pretty realistic as a lot of the data will be song_history. There will also be a relatively limited number
of platforms, since we need to add those manually.

The rest of the counts are based on real data.

## Pre-Optimization Performance Data

| Route |   Time (ms) |
| ---------------------------------------- | ------- |
| /users/create                            | 102.8   |
| /users/platform (POST)                   | 395.8   |
| /users/delete/{user_id} (POST)           | 516.8   |
|                                          |         |
| /song/get_library/ (GET)                 | 60.2    |
| /song/add (POST)                         | 100.2   |
| /song/link/add (POST)                    | 64      |
| /song/{song_id}/remove (POST)            | 695     |
| /song/{song_id}/play (GET) (No Ad)       | 208.4   |
| /song/{song_id}/play (GET) (With Ad)     | <DATA>  |
|                                          |         |
| /playlist/create (POST)                  | 70.8    |
| /playlist/{playlist_id}/songs/add (POST) | 64.8    |
| /playlist/{playlist_id}/play (GET)       | 25890.4 |
|                                          |         |
| /ad/create (POST)                        |         |

## Performance Tuning

#### Delete User

Only a single query is used:
```sql
DELETE FROM users WHERE id = :user_id
```

| QUERY PLAN                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------- |
| Delete on users  (cost=0.28..8.29 rows=0 width=0) (actual time=0.042..0.042 rows=0 loops=1)                            |
|   ->  Index Scan using users_pkey on users  (cost=0.28..8.29 rows=1 width=6) (actual time=0.027..0.028 rows=1 loops=1) |
|         Index Cond: (id = 300)                                                                                         |
| Planning Time: 0.055 ms                                                                                                |
| Trigger for constraint song_history_user_id_fkey: time=64.876 calls=1                                                  |
| Trigger for constraint users_playlist_position_user_id_fkey: time=0.325 calls=1                                        |
| Execution Time: 65.261 ms                                                                                              |

We can see this implicitly cascades the delete across the db, deleting all related records in the `song_history` and `users_playlist_position` tables.
Since `song_history` takes the longest, lets look at the query:
```sql
DELETE 
FROM song_history
WHERE user_id=:user_id
```

| QUERY PLAN                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------- |
| Delete on song_history  (cost=0.00..18262.05 rows=0 width=0) (actual time=67.680..67.681 rows=0 loops=1)             |
|   ->  Seq Scan on song_history  (cost=0.00..18262.05 rows=755 width=6) (actual time=33.211..67.582 rows=152 loops=1) |
|         Filter: (user_id = 300)                                                                                      |
|         Rows Removed by Filter: 918892                                                                               |
| Planning Time: 0.241 ms                                                                                              |
| Execution Time: 67.724 ms                                                                                            |

Woah, thats a really big sequential scan! Lets add an index on `user_id` and see if that helps to reduce the number of rows we need to scan:
```sql
CREATE INDEX song_history_user_id_index ON song_history(user_id);
```

| QUERY PLAN                                                                                                                             |
| -------------------------------------------------------------------------------------------------------------------------------------- |
| Delete on song_history  (cost=10.28..2185.37 rows=0 width=0) (actual time=0.607..0.608 rows=0 loops=1)                                 |
|   ->  Bitmap Heap Scan on song_history  (cost=10.28..2185.37 rows=755 width=6) (actual time=0.060..0.526 rows=152 loops=1)             |
|         Recheck Cond: (user_id = 300)                                                                                                  |
|         Heap Blocks: exact=142                                                                                                         |
|         ->  Bitmap Index Scan on song_history_user_id  (cost=0.00..10.09 rows=755 width=0) (actual time=0.041..0.041 rows=152 loops=1) |
|               Index Cond: (user_id = 300)                                                                                              |
| Planning Time: 0.197 ms                                                                                                                |
| Execution Time: 0.650 ms                                                                                                               |

Much better! Now we can see that the query is using the index we created, and the execution time is much lower. Let's take a look at the main query and see if this improved it.

| QUERY PLAN                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------- |
| Delete on users  (cost=0.28..8.29 rows=0 width=0) (actual time=0.047..0.047 rows=0 loops=1)                            |
|   ->  Index Scan using users_pkey on users  (cost=0.28..8.29 rows=1 width=6) (actual time=0.015..0.015 rows=1 loops=1) |
|         Index Cond: (id = 300)                                                                                         |
| Planning Time: 0.107 ms                                                                                                |
| Trigger for constraint song_history_user_id_fkey: time=0.799 calls=1                                                   |
| Trigger for constraint users_playlist_position_user_id_fkey: time=0.346 calls=1                                        |
| Execution Time: 1.217 ms                                                                                               |

Yes it did, from 65.261 ms to 1.217 ms! That's a 98% improvement.


### Delete Song

Only a single query is used:
```sql
DELETE FROM songs WHERE id = :song_id
```

| QUERY PLAN                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------- |
| Delete on songs  (cost=0.29..8.31 rows=0 width=0) (actual time=0.095..0.095 rows=0 loops=1)                            |
|   ->  Index Scan using songs_pkey on songs  (cost=0.29..8.31 rows=1 width=6) (actual time=0.015..0.016 rows=1 loops=1) |
|         Index Cond: (id = 27482)                                                                                       |
| Planning Time: 0.212 ms                                                                                                |
| Trigger for constraint links_song_id_fkey on songs: time=6.414 calls=1                                                 |
| Trigger for constraint playlist_songs_song_id_fkey on songs: time=12.478 calls=1                                       |
| Trigger for constraint song_history_song_id_fkey on songs: time=68.636 calls=1                                         |
| Trigger for constraint users_playlist_position_playlist_song_position_fkey on playlist_songs: time=0.458 calls=1       |
| Execution Time: 88.127 ms                                                                                              |

And we see a very similar story here with `song_history`, let's see what the implied query does:

```sql
DELETE FROM song_history WHERE song_id = :song_id
```

| QUERY PLAN                                                                                                        |
| ----------------------------------------------------------------------------------------------------------------- |
| Delete on song_history  (cost=0.00..18262.05 rows=0 width=0) (actual time=69.669..69.669 rows=0 loops=1)          |
|   ->  Seq Scan on song_history  (cost=0.00..18262.05 rows=27 width=6) (actual time=44.449..69.625 rows=8 loops=1) |
|         Filter: (song_id = 27482)                                                                                 |
|         Rows Removed by Filter: 919031                                                                            |
| Planning Time: 0.190 ms                                                                                           |
| Execution Time: 69.707 ms                                                                                         |

Yet another big sequential scan! Let's add an index on `song_id` and see if that helps:

```sql
CREATE INDEX song_history_song_id_index ON song_history(song_id);
```

| QUERY PLAN                                                                                                                               |
| ---------------------------------------------------------------------------------------------------------------------------------------- |
| Delete on song_history  (cost=4.63..107.86 rows=0 width=0) (actual time=9.310..9.311 rows=0 loops=1)                                     |
|   ->  Bitmap Heap Scan on song_history  (cost=4.63..107.86 rows=27 width=6) (actual time=0.020..0.029 rows=5 loops=1)                    |
|         Recheck Cond: (song_id = 27482)                                                                                                   |
|         Heap Blocks: exact=5                                                                                                             |
|         ->  Bitmap Index Scan on song_history_song_id_index  (cost=0.00..4.63 rows=27 width=0) (actual time=0.014..0.014 rows=5 loops=1) |
|               Index Cond: (song_id = 9283)                                                                                               |
| Planning Time: 0.115 ms                                                                                                                  |
| Execution Time: 9.334 ms                                                                                                                 |


And on the main query:

| QUERY PLAN                                                                                                             |
| ---------------------------------------------------------------------------------------------------------------------- |
| Delete on songs  (cost=0.29..8.31 rows=0 width=0) (actual time=0.073..0.073 rows=0 loops=1)                            |
|   ->  Index Scan using songs_pkey on songs  (cost=0.29..8.31 rows=1 width=6) (actual time=0.018..0.018 rows=1 loops=1) |
|         Index Cond: (id = 9283)                                                                                        |
| Planning Time: 0.129 ms                                                                                                |
| Trigger for constraint links_song_id_fkey on songs: time=6.389 calls=1                                                 |
| Trigger for constraint playlist_songs_song_id_fkey on songs: time=12.355 calls=1                                       |
| Trigger for constraint song_history_song_id_fkey on songs: time=0.276 calls=1                                          |
| Trigger for constraint users_playlist_position_playlist_song_position_fkey on playlist_songs: time=0.337 calls=1       |
| Execution Time: 19.472 ms                                                                                              |

Yes that did help, from 88.127 ms to 19.472 ms! That's a 78% improvement.


## Post-Optimization Performance Data
> add data here