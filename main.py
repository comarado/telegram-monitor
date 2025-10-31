import os
import asyncio
import re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

class TelegramMonitor:
    def __init__(self):
        self.api_id = int(os.getenv('APL_ID'))
        self.api_hash = os.getenv('APL_HASH')
        self.session_string = os.getenv('SESSION_STRING')
        self.target_channel = os.getenv('TARGET_CHANNEL')
        self.my_channel = os.getenv('MY_CHANNEL')
        self.keywords = os.getenv('KEYWORDS', '').split(',')
        self.phone = os.getenv('PHONE')
        
        # Очищаем и форматируем ключевые слова
        self.keywords = [kw.strip().lower() for kw in self.keywords if kw.strip()]
        
        print("🔧 Инициализация монитора...")
        print(f"🎯 Целевой канал: {self.target_channel}")
        print(f"📤 Мой канал: {self.my_channel}")
        print(f"🔍 Ключевые слова: {', '.join(self.keywords)}")
        print(f"📞 Телефон: {self.phone}")

    async def start(self):
        """Запуск мониторинга"""
        try:
            async with Client(
                "monitor_session",
                api_id=self.api_id,
                api_hash=self.api_hash,
                session_string=self.session_string,
                phone_number=self.phone
            ) as app:
                print("✅ Клиент успешно инициализирован!")
                
                # Проверяем подключение к каналам
                await self.check_channels(app)
                
                # Регистрируем обработчики
                await self.setup_handlers(app)
                
                print("🚀 Мониторинг запущен! Ожидаем новые сообщения...")
                print("=" * 60)
                
                # Бесконечный цикл для поддержания работы
                await asyncio.Future()
                
        except Exception as e:
            print(f"❌ Ошибка при запуске: {e}")
            await asyncio.sleep(10)  # Ждем перед повторной попыткой
            await self.start()  # Перезапускаем

    async def check_channels(self, app):
        """Проверяем доступ к каналам"""
        try:
            # Проверяем целевой канал
            target_chat = await app.get_chat(self.target_channel)
            print(f"✅ Доступ к целевому каналу: {target_chat.title}")
            
            # Проверяем свой канал (если указан)
            if self.my_channel:
                my_chat = await app.get_chat(self.my_channel)
                print(f"✅ Доступ к моему каналу: {my_chat.title}")
                
        except Exception as e:
            print(f"❌ Ошибка доступа к каналу: {e}")
            raise

    async def setup_handlers(self, app):
        """Настраиваем обработчики сообщений"""
        
        @app.on_message(filters.chat(self.target_channel) & filters.incoming)
        async def monitor_messages(client, message: Message):
            """Обработчик новых сообщений в целевом канале"""
            try:
                await self.process_message(message)
            except Exception as e:
                print(f"❌ Ошибка обработки сообщения: {e}")

    async def process_message(self, message: Message):
        """Обрабатываем сообщение и проверяем на ключевые слова"""
        # Получаем текст сообщения
        text = self.extract_message_text(message)
        
        if not text:
            return
            
        # Проверяем на ключевые слова
        found_keywords = self.check_keywords(text)
        
        if found_keywords:
            print(f"🎯 НАЙДЕНО СООБЩЕНИЕ С КЛЮЧЕВЫМИ СЛОВАМИ!")
            print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🔍 Найдены слова: {', '.join(found_keywords)}")
            print(f"📝 Текст: {text[:200]}...")
            print("-" * 60)
            
            # Пересылаем сообщение
            await self.forward_message(message, found_keywords)
        else:
            # Логируем все сообщения для отладки
            print(f"📨 Новое сообщение: {text[:100]}...")

    def extract_message_text(self, message: Message) -> str:
        """Извлекаем текст из сообщения"""
        text = ""
        
        if message.text:
            text = message.text
        elif message.caption:
            text = message.caption
        
        return text.lower().strip()

    def check_keywords(self, text: str) -> list:
        """Проверяем текст на наличие ключевых слов"""
        found = []
        for keyword in self.keywords:
            # Используем regex для поиска целых слов
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found.append(keyword)
        return found

    async def forward_message(self, message: Message, keywords: list):
        """Пересылаем найденное сообщение"""
        try:
            if self.my_channel:
                # Создаем заголовок с ключевыми словами
                caption = f"🎯 Найдены ключевые слова: {', '.join(keywords)}\n"
                caption += f"📅 Время: {datetime.now().strftime('%H:%M:%S')}\n"
                caption += f"🔗 Источник: {self.target_channel}"
                
                # Пересылаем сообщение
                await message.forward(
                    self.my_channel,
                    caption=caption
                )
                print(f"✅ Сообщение переслано в {self.my_channel}")
            else:
                # Если свой канал не указан, пересылаем себе
                await message.forward("me")
                print("✅ Сообщение переслано в избранное")
                
        except Exception as e:
            print(f"❌ Ошибка пересылки: {e}")

    async def get_recent_messages(self, app, limit=10):
        """Получаем последние сообщения для проверки (опционально)"""
        try:
            print(f"🔍 Проверяем последние {limit} сообщений...")
            async for message in app.get_chat_history(self.target_channel, limit=limit):
                await self.process_message(message)
        except Exception as e:
            print(f"❌ Ошибка получения истории: {e}")

async def main():
    monitor = TelegramMonitor()
    await monitor.start()

if __name__ == "__main__":
    print("🚀 Запуск Telegram монитора...")
    print("=" * 50)
    asyncio.run(main())
