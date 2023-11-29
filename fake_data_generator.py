import os
from sqlalchemy import create_engine, text
import json
import random
import argon2
import string

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

engine = create_engine("postgresql://postgres:example@localhost:61321", pool_pre_ping=True)

# Path to data dir from https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge
# also should include 1000-most-common-passwords.txt
data_path = "./data"

send_to_db = True

avid_user_percent = 0.01
avid_user_playlist_range = [20,30]
avid_user_listen_range_per_day = [10, 30]
avid_user_days_on_platform = [4, 90]

casual_user_playlist_range = [1,5]
casual_user_listen_range_per_day = [1, 10]
casual_user_days_on_platform = [1, 30]

user_good_password_chance = 0.05
good_password_length = [8, 20]

ad_campaign_num = 100
moods = ["HAPPY", "SAD", "ANGRY"]

most_common_passwords = []

with open(os.path.join(data_path, "./1000-most-common-passwords.txt")) as f:
    for line in f:
        most_common_passwords.append(line.strip())

ph = argon2.PasswordHasher()

# list all files in data_path
files = os.listdir(data_path)

songs = {}
playlists = {}
song_cnt = 0
playlist_cnt = 0
file_cnt = 0

max_songs = 10000

with engine.begin() as conn:
    # drop all tables
    conn.execute(text("""DROP TABLE IF EXISTS users_playlist_position, song_history, ad_campaigns, playlist_songs, links, playlists, users, songs, platforms;"""))

    # Create all dbs
    conn.execute(text("""
                      create table
                        public.platforms (
                            id bigint generated by default as identity,
                            platform_name text not null,
                            platform_url text not null,
                            constraint platforms_pkey primary key (id)
                        ) tablespace pg_default;

                        create table
                        public.songs (
                            id bigint generated by default as identity,
                            created_at timestamp with time zone not null default now(),
                            song_name text not null,
                            artist text not null,
                            album text not null,
                            authorization_key text not null default substr(md5((random())::text), 0, 25),
                            constraint songs_pkey primary key (id)
                        ) tablespace pg_default;

                        create table
                        public.playlists (
                            id bigint generated by default as identity,
                            name text null,
                            constraint playlists_pkey primary key (id)
                        ) tablespace pg_default;

                        create table
                        public.users (
                            id bigint generated by default as identity,
                            created_at timestamp with time zone not null default now(),
                            password text not null default 'password'::text,
                            platform_id bigint not null default '1'::bigint,
                            salt text not null default ''::text,
                            constraint users_pkey primary key (id),
                            constraint users_platform_id_fkey foreign key (platform_id) references platforms (id)
                        ) tablespace pg_default;

                        create table
                        public.links (
                            id bigint generated by default as identity,
                            created_at timestamp with time zone not null default now(),
                            song_id bigint not null,
                            platform_id bigint not null,
                            song_url text not null,
                            constraint links_pkey primary key (id),
                            constraint links_platform_id_fkey foreign key (platform_id) references platforms (id),
                            constraint links_song_id_fkey foreign key (song_id) references songs (id) on delete cascade
                        ) tablespace pg_default;

                        create table
                        public.playlist_songs (
                            playlist_id bigint not null,
                            song_id bigint not null,
                            id bigint generated by default as identity,
                            constraint playlist_songs_pkey primary key (id),
                            constraint playlist_songs_playlist_id_fkey foreign key (playlist_id) references playlists (id),
                            constraint playlist_songs_song_id_fkey foreign key (song_id) references songs (id) on delete cascade
                        ) tablespace pg_default;
                        
                        create table
                        public.ad_campaigns (
                            id bigint generated by default as identity,
                            created_at timestamp with time zone not null default now(),
                            link text not null,
                            target_mood text not null,
                            constraint ad_campaign_pkey primary key (id)
                        ) tablespace pg_default;

                        create table
                        public.song_history (
                            id bigint generated by default as identity,
                            created_at timestamp with time zone not null default now(),
                            user_id bigint not null,
                            song_id bigint not null,
                            constraint song_history_pkey primary key (id),
                            constraint song_history_song_id_fkey foreign key (song_id) references songs (id) on update cascade on delete cascade,
                            constraint song_history_user_id_fkey foreign key (user_id) references users (id) on update cascade on delete cascade
                        ) tablespace pg_default;
                        

                        create table
                        public.users_playlist_position (
                            id bigint generated by default as identity,
                            user_id bigint not null,
                            playlist_song_position bigint null,
                            playlist_id bigint null,
                            constraint users_playlist_position_pkey primary key (id),
                            constraint users_playlist_position_playlist_id_fkey foreign key (playlist_id) references playlists (id),
                            constraint users_playlist_position_playlist_song_position_fkey foreign key (playlist_song_position) references playlist_songs (id) on update restrict on delete set null,
                            constraint users_playlist_position_user_id_fkey foreign key (user_id) references users (id) on delete cascade
                        ) tablespace pg_default;"""))


# Add Spotify Platform
with engine.begin() as conn:
    conn.execute(text("""INSERT INTO platforms (platform_name, platform_url) VALUES ('Spotify', 'https://open.spotify.com%')"""))

next_song_id = 1
next_playlist_id = 1
next_playlist_song_id = 1
    # iterate through files
for file in files:
    if song_cnt > max_songs:
        break
    # open and load json file
    with open(os.path.join(data_path, file)) as json_file:
        data = json.load(json_file)
        with engine.begin() as conn:
            songs_to_insert = []
            playlists_to_insert = []
            playlist_songs_to_insert = []
            links_to_add = []
            for playlist in data["playlists"]:
                # iterate through tracks
                playlists[next_playlist_id] = []
                
                for track in playlist["tracks"]:
                    # add track to songs dict
                    if track["track_uri"] not in songs:
                        songs_to_insert.append({
                                            "song_name": track["track_name"],
                                            "artist": track["artist_name"],
                                            "album": track["album_name"]
                                        })
                        links_to_add.append({
                            "song_id": next_song_id,
                            "platform_id": 1,
                            "song_url": "https://open.spotify.com/track/" + track["track_uri"].split(":")[2]
                        })
                        songs[track["track_uri"]] = next_song_id
                        next_song_id += 1
                        song_cnt += 1
                    
                    # add track to playlists dict and to_send
                    song_id = songs[track["track_uri"]]
                    playlist_songs_to_insert.append({
                        "playlist_id": next_playlist_id,
                        "song_id": song_id
                    })
                    playlists[next_playlist_id].append((song_id, next_playlist_song_id))
                    next_playlist_song_id += 1


                next_playlist_id += 1
                playlist_cnt += 1
                playlists_to_insert.append({
                    "name": playlist["name"]
                })

            if send_to_db:
                print(f"starting send for file {file}")
                print("Starting send for songs")
                conn.execute(text("""INSERT INTO songs (song_name, artist, album) VALUES (:song_name, :artist, :album)"""),
                                        songs_to_insert)
                print(f"Finsihed sending songs - Total Songs Added: {song_cnt}")
                

                print("Starting send for playlists")
                conn.execute(text("""INSERT INTO playlists (name) VALUES (:name)"""), playlists_to_insert)
                print(f"Finsihed sending playlists - Total Playlists Added: {playlist_cnt}")

                print("Starting send for playlist_songs")
                conn.execute(text("""INSERT INTO playlist_songs (playlist_id, song_id) VALUES (:playlist_id, :song_id)"""),
                    playlist_songs_to_insert)
                print(f"Finished playlist_songs - Total Playlist Songs Added: {len(playlist_songs_to_insert)}")
                print("finished send for file {file}")

                print("Starting to add links")
                conn.execute(text("""INSERT INTO links (song_id, platform_id, song_url) VALUES (:song_id, :platform_id, :song_url)"""), links_to_add)
                print(f"Finished adding links - Total Links Added: {len(links_to_add)}")

            else:
                print("skipping send because send_to_db is False")
                print(f"Total Songs Added: {song_cnt}")
                print(f"Total Playlists Added: {playlist_cnt}")
                print(f"Total Playlist Songs Added: {len(playlist_songs_to_insert)}")

    file_cnt += 1

print("Completed adding Songs + Playlists")

playlist_not_made_by_user = playlist_cnt

# add users based on ratios
users_cnt = 0
next_user_idx = 1

users_to_add = []
playlist_position_to_add = []
playlist_song_history_to_add = []

playlist_song_history_per_user = []

print("Starting user creation")
with engine.begin() as conn:
    while playlist_not_made_by_user > 0:
        # choose avid or casual user
        if random.random() < avid_user_percent:
            # Avid User
            num_playlists_created = random.randint(avid_user_playlist_range[0], avid_user_playlist_range[1])


        else:
            # Casual User
            num_playlists_created = random.randint(casual_user_playlist_range[0], casual_user_playlist_range[1])

        playlist_not_made_by_user -= num_playlists_created

        user_song_history = []
        
        # Assign playlists
        for i in range(num_playlists_created):
            if len(playlists) == 0:
                break
            # select random playlist
            playlist_id = next(iter(playlists.keys()))
            playlist_songs = playlists.pop(playlist_id)

            # select random position
            playlist_song_position_idx = random.randint(0, len(playlist_songs)-1)
            playlist_song_position_id = playlist_songs[playlist_song_position_idx][1]

            # they played all songs before that
            for playlist_idx in range(playlist_song_position_idx):
                user_song_history.append({
                    "user_id": next_user_idx,
                    "song_id": playlist_songs[playlist_idx][0]
                })

            # create user_playlist_position
            playlist_position_to_add.append({
                "playlist_id": playlist_id,
                "playlist_song_position": playlist_song_position_id,
                "user_id": next_user_idx
            })
        
        # add song history
        playlist_song_history_per_user.append(user_song_history)

        # select password
        if random.random() < user_good_password_chance:
            length = random.randint(good_password_length[0], good_password_length[1])
            password = get_random_string(length)
        else:
            password = random.choice(most_common_passwords)

        hash = ph.hash(password)

        # create user
        users_to_add.append({
            "password": hash
        })

        users_cnt += 1
        next_user_idx += 1

        if users_cnt % 50 == 0:
            print(f"...Created {users_cnt} users")

    print(f"Finished creating users - Total Users: {users_cnt}")

    print("Starting song history creation")
    # add song history, each user will go in order, but the order of users is random for each new user
    while len(playlist_song_history_per_user) > 0:
        # random user index
        user_idx = random.randint(0, len(playlist_song_history_per_user)-1)

        if len(playlist_song_history_per_user[user_idx]) == 0:
            playlist_song_history_per_user.pop(user_idx)

        # get next song for user
        user_song_record = playlist_song_history_per_user[user_idx].pop(0)

        if len(playlist_song_history_per_user[user_idx]) == 0:
            playlist_song_history_per_user.pop(user_idx)

        playlist_song_history_to_add.append(user_song_record)

    print("Finished song history creation")

    # Add users to db
    if send_to_db:
        print("starting user send of {users_cnt} users")
        conn.execute(text("""INSERT INTO users (password, platform_id) VALUES (:password, 1)"""), users_to_add)
        print(f"finished user send - Added {users_cnt} users")

        print("starting playlist_position send")
        conn.execute(text("""INSERT INTO users_playlist_position (playlist_id, playlist_song_position, user_id) VALUES (:playlist_id, :playlist_song_position, :user_id)"""), playlist_position_to_add)
        print(f"finished playlist_position send - Added {len(playlist_position_to_add)} playlist_positions")

        print("starting song_history send")
        conn.execute(text("""INSERT INTO song_history (user_id, song_id) VALUES (:user_id, :song_id)"""), playlist_song_history_to_add)
        print(f"finished song_history send - Added {len(playlist_song_history_to_add)} song_history")
    else:
        print("skipping user send because send_to_db is False")
        print(f"Total Users: {users_cnt}")
        print(f"Sample Password: {users_to_add[0]['password']}")




# add ad campaigns
ad_campaigns_to_add = []

for i in range(ad_campaign_num):
    random_mood = random.choice(moods)
    url_salt = get_random_string(10)

    if random_mood == "HAPPY":
        url = "https://en.wikipedia.org/wiki/Happiness#" + url_salt
    elif random_mood == "SAD":
        url = "https://en.wikipedia.org/wiki/Sadness#" + url_salt
    else:
        url = "https://en.wikipedia.org/wiki/Anger#" + url_salt

    ad_campaigns_to_add.append({
        "link": url,
        "target_mood": random_mood
    })

with engine.begin() as conn:
    if send_to_db:
        print("starting ad_campaign send")
        conn.execute(text("""INSERT INTO ad_campaigns (link, target_mood) VALUES (:link, :target_mood)"""), ad_campaigns_to_add)
        print(f"finished ad_campaign send - Added {len(ad_campaigns_to_add)} ad_campaigns")
    else:
        print("skipping ad_campaign send because send_to_db is False")
        print(f"Total Ad Campaigns: {len(ad_campaigns_to_add)}")


total_rows = song_cnt + playlist_cnt + users_cnt + len(playlist_position_to_add) + len(playlist_song_history_to_add) + len(ad_campaigns_to_add) + len(links_to_add)
print(f"Total Rows: {total_rows}")