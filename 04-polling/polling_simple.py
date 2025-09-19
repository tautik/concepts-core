from fastapi import FastAPI
import sqlite3
import time
import asyncio
import uvicorn

app = FastAPI()

def get_user_status(user_id: str) -> dict:
    conn = sqlite3.connect("sharding.db")
    cursor = conn.cursor()
    cursor.execute('SELECT last_heartbeat FROM heartbeats WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and (time.time() - result[0]) <= 30:
        return {"status": "active", "last_heartbeat": result[0]}
    return {"status": "inactive", "last_heartbeat": None}

# SHORT POLL: Client pings every second
@app.get("/short-poll/{user_id}")
async def short_poll(user_id: str):
    return get_user_status(user_id)

# LONG POLL: Server checks internally until change or timeout
@app.get("/long-poll/{user_id}")
async def long_poll(user_id: str):
    for _ in range(30):  # Check for 30 seconds
        status = get_user_status(user_id)
        if status["status"] == "active":
            return status
        await asyncio.sleep(1)
    
    return get_user_status(user_id)  # Return final status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
