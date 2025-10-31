import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from keep_alive import keep_alive

# 🔹 Получаем данные из переменных окружения Render
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
session_string = os.getenv("SESSION_STRING")
my_chat_id = os.getenv("MY_CHAT_ID")  # может быть ID или @username
keywords = os.getenv("KEYWORDS", "").split(",")  # например: макбук,айфон,ps5

# 🔹 Запускаем Flask-сервер для Render
keep_alive()

# 🔹 Подключаемся к Telegram
if bot_token:
    print("🤖 Запускаем через бот-токен...")
    client = TelegramClient("bot", api_id, api_hash).start(bot_token=bot_token)
elif session_string:
    print("👤 Запускаем через session string...")
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    client.start()
else:
    raise ValueError("❌ Не найден BOT_TOKEN или SESSION_STRING в окружении!")

# 🔹 Функция отправки сообщений себе
async def send_to_me(text):
    try:
        await client.send_message(my_chat_id, text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# 🔹 Мониторинг сообщений с ключевыми словами
@client.on(events.NewMessage)
async def handler(event):
    text = event.raw_text.lower()
    for kw in keywords:
        if kw.strip().lower() in text:
            msg = f"🔎 Совпадение по ключевому слову «{kw.strip()}»:\n\n{text}\n\n👉 {event.message.link if event.message else ''}"
            await send_to_me(msg)
            break

print("🚀 Telegram монитор запущен…")
client.run_until_disconnected()
