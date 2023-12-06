import sqlalchemy
from src import database as db
import json
import requests
import os
import queue
import threading

q = queue.Queue()

def gen_mood(user_id) -> str:
    with db.engine.begin() as conn:
        result = conn.execute(sqlalchemy.text("""
                SELECT COUNT(*) FROM song_history
                WHERE user_id = :user_id
                """),
                [{
                    "user_id": user_id
                }]).scalar_one()
        
        if result < 5:
            return None
        
        result = conn.execute(sqlalchemy.text("""
                SELECT song_name, artist
                FROM song_history
                JOIN songs ON song_history.song_id = songs.id
                WHERE user_id = 23
                ORDER BY song_history.created_at DESC
                LIMIT 5
                """)).all()
    
    song_prompt = "Classify the user's mood based on song titles into only one of these emotions: Sad, Happy, Angry. The response should be the most likely mood as one word. \n\n#### Songs\n"
    for song in result:
        song_prompt += song.song_name + " by " + song.artist + "\n"

    payload = json.dumps({
        "model": "llama2-uncensored",
        "prompt": song_prompt,
        "stream": False,
        "temperature": 0,
        "template": "{{ .System }}\n\n### HUMAN:\n{{ .Prompt }}\n\n### RESPONSE:\nThe most likely mood is "
        })
    headers = {
    'Content-Type': 'application/json'
    }

    print("Getting Sentiment from OLLAMA")

    response = requests.request("POST", os.environ.get("OLLAMA_URI"), headers=headers, data=payload)
    response = response.json()
    print(response)

    mood = ""
    if "happy" in response["response"].lower():
        mood = "HAPPY"
    elif "sad" in response["response"].lower():
        mood = "SAD"
    elif "angry" in response["response"].lower():
        mood = "ANGRY"

    if mood == "":
        return None
    return mood

def thread_func(jobs=queue.Queue):
    print("ollama runner daemon started...")
    while True:
        # there is a job
        user_id = jobs.get()
        with db.engine.begin() as conn:
            result = conn.execute(sqlalchemy.text("""
                SELECT COUNT(*)
                FROM song_history
                WHERE user_id = :user_id
                                                    """),
                [{
                    "user_id":user_id
                }]).scalar_one_or_none()
        if result is None or result < 5:
            continue
        else:
            mood = gen_mood(user_id)
            with db.engine.begin() as conn:
                conn.execute(sqlalchemy.text("""
                INSERT INTO user_moods(mood, songs_played,user_id)
                VALUES(:mood, 0, :user_id)
                ON CONFLICT (user_id)
                DO UPDATE SET 
                    last_updated=now(), 
                    mood=:mood, 
                    songs_played=0
                WHERE user_moods.user_id = :user_id
                                                """
                                                    ), [{
                    "user_id": user_id,
                    "mood":mood
                }])
                
def start_daemon():
    t = threading.Thread(daemon=True, target=thread_func, args=(q,))
    t.start()
