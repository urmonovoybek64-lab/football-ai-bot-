
import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Assalomu alaykum! ⚽ Futbol AI bot ishga tushdi."
    )

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "Bot tez orada futbol tahlillarini yuboradi.")

print("Bot ishga tushdi!")
bot.infinity_polling()
