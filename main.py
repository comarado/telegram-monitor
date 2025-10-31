import os
import asyncio
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread
#from dotenv import load_dotenv

#load_dotenv()

# Настройки из .env
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
target_channels = [ch.strip() for ch in os.getenv('TARGET_CHANNEL', '').split(',') if ch.strip()]
my_channel = os.getenv('MY_CHANNEL')
keywords = [kw.strip() for kw in os.getenv('KEYWORDS', '').split(',') if kw.strip()]

client = TelegramClient('session', api_id, api_hash)

async def forward_complete_message(event):
    """Пересылает полное сообщение с ссылкой и информацией об авторе"""
    message = event.message
    sender = await message.get_sender()
    chat = await event.get_chat()

    # Получаем информацию об авторе
    if sender:
        if hasattr(sender, 'username') and sender.username:
            author_info = f"👤 {sender.first_name or ''} {sender.last_name or ''} (@{sender.username})"
        else:
            author_info = f"👤 {sender.first_name or ''} {sender.last_name or ''} (ID: {sender.id})"
    else:
        author_info = "👤 Неизвестный отправитель"

    # Определяем тип чата и создаем ссылку
    if hasattr(chat, 'title'):
        # Это канал/группа
        chat_name = chat.title
        message_link = f"https://t.me/c/{str(chat.id).replace('-100', '')}/{message.id}"
        source_info = f"📅 Канал: {chat_name}"
    else:
        # Это личное сообщение
        chat_name = f"{chat.first_name or ''} {chat.last_name or ''}".strip()
        message_link = f"tg://openmessage?user_id={chat.id}&message_id={message.id}"
        source_info = f"💬 Личное сообщение от: {chat_name}"

    # Создаем информационное сообщение
    caption = (
        f"🔔 **Найдено совпадение!**\n\n"
        f"{author_info}\n"
        f"{source_info}\n"
        f"🔗 [Перейти к сообщению]({message_link})\n"
        f"⏰ {message.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
    )

    try:
        # Если есть медиа
        if message.media:
            if message.text:
                caption += f"\n{message.text}"

            await client.send_message(
                my_channel,
                caption,
                file=message.media,
                link_preview=False
            )
        else:
            # Если только текст
            caption += f"\n{message.text}"
            await client.send_message(
                my_channel,
                caption,
                link_preview=False
            )

        print(f"✅ Сообщение переслано от: {chat_name}")

    except Exception as e:
        # Если не удалось переслать медиа
        error_message = (
            f"{caption}\n\n"
            f"📄 **Текст:**\n{message.text or 'Нет текста'}\n\n"
            f"⚠️ *Не удалось переслать вложения*\n"
            f"🔗 [Открыть оригинал]({message_link})"
        )
        await client.send_message(my_channel, error_message)
        print(f"⚠️ Ошибка пересылки от {chat_name}: {e}")

@client.on(events.NewMessage)
async def handler(event):
    """Обработчик ВСЕХ новых сообщений"""
    try:
        chat = await event.get_chat()
        message_text = event.message.text or ""

        # Определяем откуда сообщение
        if hasattr(chat, 'title'):
            # Это канал/группа
            chat_name = chat.title
            chat_username = f"@{chat.username}" if hasattr(chat, 'username') and chat.username else chat_name

            # Проверяем, что сообщение из нужного канала
            if chat_username in target_channels or chat_name in target_channels:
                # Проверяем ключевые слова
                if any(keyword in message_text.lower() for keyword in keywords):
                    print(f"🔍 Найдено ключевое слово в канале: {chat_name}")
                    await forward_complete_message(event)
        else:
            # Это личное сообщение от пользователя
            chat_name = f"{chat.first_name or ''} {chat.last_name or ''}".strip()

            # Проверяем ключевые слова в личных сообщениях
            if any(keyword in message_text.lower() for keyword in keywords):
                print(f"🔍 Найдено ключевое слово в ЛС от: {chat_name}")
                await forward_complete_message(event)

    except Exception as e:
        print(f"❌ Ошибка обработки сообщения: {e}")

# Flask для поддержания активности
app = Flask('')

@app.route('/')
def home():
    return "✅ Telegram Monitor is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def main():
    await client.start(phone)

    # Проверяем доступ к каналам
    print("🚀 Мониторинг запущен!")
    print(f"📊 Ключевые слова: {keywords}")
    print(f"📺 Отслеживаемые каналы: {target_channels}")
    print("💬 Также мониторятся ЛИЧНЫЕ СООБЩЕНИЯ от пользователей")

    for channel in target_channels:
        if channel:
            try:
                entity = await client.get_entity(channel)
                if hasattr(entity, 'title'):
                    print(f"✅ Доступ к каналу: {entity.title}")
                else:
                    print(f"✅ Доступ к пользователю: {entity.first_name}")
            except Exception as e:
                print(f"❌ Нет доступа к {channel}: {e}")

    await client.run_until_disconnected()

if __name__ == '__main__':
    # Запускаем Flask в фоне
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Запускаем Telethon
    asyncio.run(main())

