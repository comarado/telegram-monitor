from pyrogram import Client
import os
from dotenv import load_dotenv

load_dotenv()

async def generate_session_string():
    async with Client(
        "my_session",
        api_id=os.getenv("API_ID"),
        api_hash=os.getenv("API_HASH")
    ) as app:
        session_string = await app.export_session_string()
        print("\n" + "="*50)
        print("ВАШ SESSION_STRING:")
        print("="*50)
        print(session_string)
        print("="*50)
        print("\n⚠️ Сохраните эту строку в переменную SESSION_STRING в Render!")
        print("Больше НЕ запускайте этот скрипт!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_session_string())