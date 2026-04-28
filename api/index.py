import telebot
import random
from http.server import BaseHTTPRequestHandler

# Твой токен
TOKEN = '8708041665:AAEwbW52DA-zIiarX4eGWesDsxp5hOypjh4'
bot = telebot.TeleBot(TOKEN, threaded=False)

# Временный словарик для хранения параметров фокуса (работает пока жива функция)
# В идеале для 100% надежности нужны БД, но для тестов и быстрых ответов этого хватит
user_data = {}

@bot.message_handler(commands=['start'])
def start_magic(message):
    # Генерируем случайные параметры
    # Формула в итоге: ((x * m1) + a1) * m2 - a2
    m1 = random.randint(2, 4)  # Первый множитель
    a1 = random.randint(5, 15) # Первое слагаемое
    a2 = random.randint(5, 15) # Второе вычитаемое
    
    # Сохраняем параметры для этого пользователя
    user_data[message.chat.id] = {'m': m1, 'shift': a1 * 1 - a2} 
    # Упрощенная логика: мы дадим фиксированную структуру, но со случайными числами
    
    instructions = (
        "🎲 **Новая игра — новые числа!**\n\n"
        "Считай внимательно:\n"
        f"1. Загадай число.\n"
        f"2. Умножь его на **{m1}**.\n"
        f"3. Прибавь к результату **{a1}**.\n"
        f"4. Вычти из того, что получилось, **{a2}**.\n"
        f"5. Прибавь еще **{random.randint(1, 10)}** (шучу, это просто для веса).\n\n"
        "Напиши итоговый результат!"
    )
    
    # Чтобы не усложнять, сделаем 5 шагов со случайными числами, 
    # но будем хранить итоговое смещение
    
    # Генерируем 5-6 случайных операций
    current_coeff = 1
    current_sum = 0
    text_steps = ["1. Загадай целое число."]
    
    for i in range(2, 8):
        op = random.choice(['+', '-', '*'])
        val = random.randint(2, 10)
        
        if op == '+':
            current_sum += val
            text_steps.append(f"{i}. Прибавь {val}.")
        elif op == '-':
            current_sum -= val
            text_steps.append(f"{i}. Вычти {val}.")
        elif op == '*':
            current_coeff *= val
            current_sum *= val
            text_steps.append(f"{i}. Умножь всё на {val}.")
            
    # Сохраняем итоговую формулу: Результат = x * coeff + sum
    user_data[message.chat.id] = {'c': current_coeff, 's': current_sum}
    
    full_text = "🎩 **Магия начинается!**\n\n" + "\n".join(text_steps) + "\n\n**Напиши, что получилось в итоге?**"
    bot.send_message(message.chat.id, full_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        bot.reply_to(message, "Нажми /start, чтобы начать новый фокус!")
        return

    try:
        res = float(message.text.replace(',', '.'))
        data = user_data[chat_id]
        
        # Обратный расчет: x = (Результат - sum) / coeff
        original = (res - data['s']) / data['c']
        
        bot.send_chat_action(chat_id, 'typing')
        import time
        time.sleep(1)
        
        bot.send_message(chat_id, f"🔮 Хм... Математические волны говорят мне, что ты загадал число **{int(round(original))}**!")
        # Очищаем данные после отгадывания
        del user_data[chat_id]
        
    except Exception:
        bot.send_message(chat_id, "Напиши число ответом на загадку!")

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
        self.wfile.write("Random Magic is Online!".encode())
