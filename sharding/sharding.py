from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import time
import uvicorn


app = FastAPI()

DB_NAMES = ["sharding.db", "sharding2.db"]
    
class HeartBeatRequest(BaseModel):
    user_id: str


def get_shard_index(request: HeartBeatRequest) -> int:
    user_id = request.user_id
    if user_id == "1":
        return 0
    elif user_id == "2":
        return 1;
    else:
        return 0

def init_db():
    for db_name in DB_NAMES:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS heartbeats (
            user_id TEXT PRIMARY KEY,
            last_heartbeat INTEGER
        )
        ''')

        conn.commit()
        conn.close()

@app.post("/heartbeat")
async def post_heartbeat(request: HeartBeatRequest):
    shard_index = get_shard_index(request.user_id)
    db_name = DB_NAMES[shard_index]

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
    REPLACE INTO heartbeats (user_id, last_heartbeat) VALUES (?, ?)
    ''', (request.user_id, int(time.time())))

    conn.commit()
    conn.close()

    return {"message": "Heartbeat recorded successfully"}

@app.get("/heartbeat/status/{user_id}")
async def get_heartbeat_status(user_id: str):
    shard_index = get_shard_index(user_id)
    db_name = DB_NAMES[shard_index]

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(''' SELECT last_heartbeat FROM heartbeats WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {"status": "active", "last_heartbeat": result[0]}
    else:
        return {"status": "inactive", "last_heartbeat": None}
    

if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=9000)
