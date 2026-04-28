from http.server import BaseHTTPRequestHandler
import telebot
import random

TOKEN = '8708041665:AAEwbW52DA-zIiarX4eGWesDsxp5hOypjh4'
bot = telebot.TeleBot(TOKEN, threaded=False)

# Временная память (в бесплатном Vercel она сбрасывается, 
# для фокуса в один шаг это ок)
@bot.message_handler(commands=['start'])
def start(message):
    m = random.randint(2, 5)
    s = random.randint(1, 20)
    # Мы можем зашифровать ответ в самой инструкции, 
    # чтобы боту не нужно было ничего запоминать!
    msg = (f"🎩 Магия!\n1. Загадай число.\n2. Умножь на {m}.\n"
           f"3. Прибавь {s}.\n4. Умножь на 2.\n"
           f"Напиши итог!")
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: True)
def answer(message):
    try:
        res = float(message.text)
        # Здесь должна быть формула обратного счета
        bot.send_message(message.chat.id, "🔮 Ты загадал число...")
    except:
        bot.send_message(message.chat.id, "Напиши число цифрами!")

class handler(BaseHTTPRequestHandler):
    def doPost(self):
        # Этот блок нужен Vercel, чтобы принять сообщение от Telegram
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = telebot.types.Update.de_json(post_data.decode('utf-8'))
        bot.process_new_updates([update])
        self.send_response(200)
        self.end_headers()
