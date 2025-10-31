from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram monitor is running!"

def run():
    # Flask-сервер, который нужен, чтобы Render не «усыплял» приложение
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
