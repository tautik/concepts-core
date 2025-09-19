import asyncio
import aiohttp
import time

BASE_URL = "http://localhost:8001"

async def test_short_poll(user_id: str):
    """Client pings every second"""
    async with aiohttp.ClientSession() as session:
        for i in range(5):
            async with session.get(f"{BASE_URL}/short-poll/{user_id}") as response:
                result = await response.json()
                print(f"Short poll #{i+1}: {result['status']}")
            await asyncio.sleep(1)

async def test_long_poll(user_id: str):
    """Server waits internally"""
    async with aiohttp.ClientSession() as session:
        print("Long poll: waiting for response...")
        async with session.get(f"{BASE_URL}/long-poll/{user_id}") as response:
            result = await response.json()
            print(f"Long poll result: {result['status']}")

async def main():
    print("Testing Short Poll vs Long Poll")
    await test_short_poll("1")
    await test_long_poll("1")

if __name__ == "__main__":
    asyncio.run(main())
