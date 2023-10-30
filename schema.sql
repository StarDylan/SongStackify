
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
    constraint songs_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.users (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    password text not null default 'password'::text,
    platform_id bigint not null default '1'::bigint,
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
    constraint links_song_id_fkey foreign key (song_id) references songs (id)
  ) tablespace pg_default;

  create table
  public.playlists (
    id bigint generated by default as identity,
    name text null,
    current_song_idx bigint not null default '-1'::bigint,
    constraint playlists_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.playlist_songs (
    playlist_id bigint not null,
    song_id bigint not null,
    constraint playlist_songs_pkey primary key (playlist_id, song_id),
    constraint playlist_songs_playlist_id_fkey foreign key (playlist_id) references playlists (id),
    constraint playlist_songs_song_id_fkey foreign key (song_id) references songs (id)
  ) tablespace pg_default;
  
  
  
  INSERT INTO songs (song_name, artist, album)
  VALUES ('Mr. Brightside', 'The Killers', 'Hot Fuss');

  INSERT INTO platforms (platform_name, platform_url)
  VALUES ('Spotify', 'open.spotify.com');

  INSERT INTO links (song_id, platform_id, song_url)
  VALUES (1, 1, 'https://open.spotify.com/track/003vvx7Niy0yvhvHt4a68B?si=095e444ca83840c7');

  INSERT INTO playlists (name)
  VALUES ('My Amazing Playlist');

  INSERT INTO playlist_songs (playlist_id, song_id)
  VALUES (1, 1);