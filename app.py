from flask import Flask, request, jsonify
import telebot
import os
import logging
import time

app = Flask(__name__)

# Настройка бота
TOKEN = os.environ.get('7936477847:AAGFEZeSzqqoeLLvcgjd_fMW56-_zdXx5_0')  # Получите токен от @BotFather
bot = telebot.TeleBot(TOKEN)


# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Обработчики команд бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой бот на Flask и Render! 👋\n"
                          "Используй /help для списка команд")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    📋 Доступные команды:
    /start - Начать работу с ботом
    /help - Показать это сообщение
    /about - Информация о боте
    /echo [текст] - Повторить текст
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['about'])
def about(message):
    bot.reply_to(message, "🤖 Этот бот работает на:\n"
                          "- Python Flask\n"
                          "- Telebot\n"
                          "- Render.com\n"
                          "🔄 Работает 24/7 благодаря вебхукам и мониторингу")

@bot.message_handler(commands=['echo'])
def echo(message):
    try:
        text = message.text.split(' ', 1)[1]
        bot.reply_to(message, f"🔁 Вы сказали: {text}")
    except IndexError:
        bot.reply_to(message, "❌ Напишите текст после команды /echo")

# Вебхук для Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        if request.headers.get('content-type') == 'application/json':
            json_data = request.get_json()
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
            return jsonify({"status": "ok"}), 200
        return jsonify({"error": "Invalid content type"}), 403
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

# Главная страница
@app.route('/')
def hello_world():
    return '🤖 Telegram Bot is running! Visit /status for bot status'

# Статус бота
@app.route('/status')
def status():
    if TOKEN:
        try:
            webhook_info = bot.get_webhook_info()
            bot_info = bot.get_me()
            return jsonify({
                "status": "running",
                "webhook_set": webhook_info.url,
                "bot_username": bot_info.username
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"status": "running", "message": "Token not configured"})

# Для поддержания активности
@app.route('/ping')
def ping():
    return "pong", 200

# Установка вебхука при запуске
def set_webhook():
    if TOKEN and os.environ.get('RENDER_EXTERNAL_HOSTNAME'):
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook установлен на: {webhook_url}")
        except Exception as e:
            logger.error(f"Ошибка при установке вебхука: {e}")

# Устанавливаем вебхук при запуске приложения
set_webhook()

if __name__ == '__main__':
    # Для локального тестирования без вебхука
    if TOKEN:
        bot.polling(non_stop=True)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)
