import telebot
import random
import time
from telebot import types
from http.server import BaseHTTPRequestHandler

# Твой токен
TOKEN = '8708041665:AAEwbW52DA-zIiarX4eGWesDsxp5hOypjh4'
bot = telebot.TeleBot(TOKEN, threaded=False)

user_data = {}

def get_magic_markup():
    """Создает кнопку для повторного старта"""
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🔄 Попробовать еще раз", callback_data="restart")
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start'])
def start_magic(message):
    send_magic_steps(message.chat.id)

def send_magic_steps(chat_id):
    """Основная логика генерации фокуса"""
    current_coeff = 1
    current_sum = 0
    
    bot.send_chat_action(chat_id, 'typing')
    steps = ["1️⃣ Загадай любое целое число."]
    
    for i in range(2, 7):
        op = random.choice(['+', '-', '*'])
        val = random.randint(2, 7) # Уменьшил диапазон, чтобы числа не были слишком гигантскими
        
        if op == '+':
            current_sum += val
            steps.append(f"{i}️⃣ Прибавь **{val}**")
        elif op == '-':
            current_sum -= val
            steps.append(f"{i}️⃣ Вычти **{val}**")
        elif op == '*':
            current_coeff *= val
            current_sum *= val
            steps.append(f"{i}️⃣ Умножь результат на **{val}**")
            
    user_data[chat_id] = {'c': current_coeff, 's': current_sum}
    
    instructions = (
        "📜 **Твой магический свиток заданий:**\n\n" + 
        "\n".join(steps) + 
        "\n\n✨ Когда закончишь вычисления, **напиши мне итог!**"
    )
    bot.send_message(chat_id, instructions, parse_mode="Markdown")

# Обработка нажатия на кнопку "Еще раз"
@bot.callback_query_handler(func=lambda call: call.data == "restart")
def callback_restart(call):
    # Убираем "часики" с кнопки
    bot.answer_callback_query(call.id)
    # Запускаем фокус заново
    send_magic_steps(call.message.chat.id)

@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.send_message(chat_id, "💫 Нажми /start, чтобы начать магию!")
        return

    try:
        res = float(message.text.strip().replace(',', '.'))
        data = user_data[chat_id]
        original = (res - data['s']) / data['c']
        
        msg = bot.send_message(chat_id, "🌀 *Считываю твою ауру...*", parse_mode="Markdown")
        time.sleep(1.2)
        
        final_text = (
            f"🎯 **ГОТОВО!**\n\n"
            f"Ты загадал число: 🔥 **{int(round(original))}** 🔥\n\n"
            f"Хочешь проверить меня снова?"
        )
        # Отправляем результат вместе с кнопкой
        bot.edit_message_text(final_text, chat_id, msg.message_id, 
                              parse_mode="Markdown", 
                              reply_markup=get_magic_markup())
        
        del user_data[chat_id]
        
    except Exception:
        bot.send_message(chat_id, "🎭 Магия любит точность! Пришли число цифрами.")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = telebot.types.Update.de_json(post_data.decode('utf-8'))
        bot.process_new_updates([update])
        self.send_response(200)
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write("Magic Bot with Buttons is Ready!".encode())
