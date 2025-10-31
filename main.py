from keep_alive import keep_alive
keep_alive()
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread
import requests
import os

# === Настройки окружения ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = "monitor"
target_chat = os.getenv("TARGET_CHAT")  # ID или username канала для мониторинга
my_chat_id = int(os.getenv("MY_CHAT_ID"))  # куда присылать совпадения
keywords = [x.strip().lower() for x in os.getenv("KEYWORDS", "макбук,iphone,айфон").split(",")]

# === Flask для keep-alive ===
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram monitor is running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_web).start()

# === Telegram Client ===
client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(chats=target_chat))
async def handler(event):
    text = event.message.message.lower()
    if any(k in text for k in keywords):
        msg = f"🔍 Найдено совпадение:\n\n{text}"
        print(msg)
        try:
            await client.send_message(my_chat_id, msg)
        except Exception as e:
            print("Ошибка отправки:", e)

print("🚀 Telegram монитор запущен…")
client.start()
client.run_until_disconnected()

