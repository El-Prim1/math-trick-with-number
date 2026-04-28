import os
import telebot
from http.server import BaseHTTPRequestHandler

# Вставь свой токен прямо сюда между кавычек для теста
TOKEN = 'ТВОЙ_ТОКЕН_ТУТ'
bot = telebot.TeleBot(TOKEN, threaded=False)

# Функция для обработки сообщений Telegram
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎩 Привет! Я твой бот-фокусник. Скоро я буду угадывать твои числа!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Ты написал: {message.text}. Пока я просто повторяю за тобой, но скоро научусь магии!")

# Главный обработчик для Vercel
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("<h1>Бот запущен и готов к работе!</h1>".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = telebot.types.Update.de_json(post_data.decode('utf-8'))
        bot.process_new_updates([update])
        self.send_response(200)
        self.end_headers()
