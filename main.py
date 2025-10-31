import os
import asyncio
from pyrogram import Client, filters
from dotenv import load_dotenv

load_dotenv()

async def generate_and_exit():
    """Генерирует session_string и завершает работу"""
    print("🔐 Генерация session_string...")
    
    async with Client(
        "session_generator",
        api_id=int(os.getenv("API_ID")),
        api_hash=os.getenv("API_HASH")
    ) as app:
        session_string = await app.export_session_string()
        
        print("\n" + "="*60)
        print("✅ SESSION_STRING УСПЕШНО СГЕНЕРИРОВАН!")
        print("="*60)
        print(session_string)
        print("="*60)
        print("\n⚠️ Скопируйте эту строку и добавьте в Render как SESSION_STRING")
        print("Затем перезапустите сервис без параметра GENERATE_SESSION")
        
    # Завершаем работу после генерации
    return session_string

async def main_app():
    """Основной рабочий режим"""
    async with Client(
        "my_account",
        api_id=int(os.getenv("API_ID")),
        api_hash=os.getenv("API_HASH"),
        session_string=os.getenv("SESSION_STRING")
    ) as app:
        print("✅ Бот запущен в рабочем режиме!")
        
        @app.on_message(filters.chat("@MagicSchoolBA"))
        async def handle_magic_school(client, message):
            await message.forward("me")
            print(f"📨 Получено сообщение: {message.text}")
        
        await asyncio.Future()

async def main():
    # Проверяем, нужно ли генерировать сессию
    if os.getenv("GENERATE_SESSION") == "true":
        await generate_and_exit()
    else:
        if not os.getenv("SESSION_STRING"):
            print("❌ SESSION_STRING не найден!")
            print("Добавьте переменную GENERATE_SESSION=true для генерации")
            return
        await main_app()

if __name__ == "__main__":
    asyncio.run(main())
