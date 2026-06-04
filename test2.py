
import telebot
import random
from telebot import types
import emoji

TOKEN = "BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)


# ===============================
# ЗАГРУЗКА ФАКТОВ ИЗ ФАЙЛА ОДИН РАЗ
# ===============================

def load_spain_facts():
    facts_dict = {}

    with open("Spain.txt", "r", encoding="utf-8") as file:
        for line in file:
            club, facts = line.strip().split("|")
            facts_dict[club] = [f.strip() for f in facts.split(";")]

    return facts_dict
SPAIN_FACTS = load_spain_facts()   # Загружаем факты при запуске

def load_england_facts():
    facts_dict = {}

    with open("England.txt", "r", encoding="utf-8") as file:
        for line in file:
            club, facts = line.strip().split("|")
            facts_dict[club] = [f.strip() for f in facts.split(";")]
    return facts_dict
ENGLAND_FACTS = load_england_facts()   # Загружаем факты при запуске


# ===============================
# КОМАНДА START
# ===============================
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 England", "🇪🇸 Spain")
    bot.send_message(
        message.chat.id,
        "Давай выберем лигу:",
        reply_markup=markup
    )


# ===============================
# ОБРАБОТКА ТЕКСТА
# ===============================
@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    # ===== ВЫБОР ЛИГИ =====
    if message.text == "🇬🇧 England":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🇬🇧 Liverpool", "🇬🇧 Arsenal")
        bot.send_message(
            message.chat.id,
            "Отлично, теперь выбери клуб",
            reply_markup=markup
        )

    elif message.text == "🇪🇸 Spain":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🇪🇸 Barcelona", "🇪🇸 Real Madrid")
        bot.send_message(
            message.chat.id,
            "Отлично, теперь выбери клуб",
            reply_markup=markup
        )

    # ===== ВЫБОР БАРСЕЛОНЫ =====
    elif message.text == "🇪🇸 Barcelona":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("👀 Интересный факт")

        bot.send_message(
            message.chat.id,
            "«Visca el Barça i Visca Catalunya!» - «Да здравствует «Барса» и да здравствует Каталония!»"
            "\n Что хочешь узнать?",
            reply_markup=markup
        )

    # ===== ВЫДАЧА ФАКТА =====
    elif message.text == "👀 Интересный факт":

        barca_facts = SPAIN_FACTS.get("Barcelona")

        if barca_facts:
            fact = random.choice(barca_facts)
            bot.send_message(message.chat.id, fact)
        else:
            bot.send_message(message.chat.id, "Факты не найдены 😢")

    elif message.text == "🇪🇸 Real Madrid":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("👀 Интересный факт")
        bot.send_message(
            message.chat.id,
            "«Hala Madrid! - Да здравствует Мадрид!»"
            "\n Что хочешь узнать?",
            reply_markup=markup
        )

    # ===== ВЫДАЧА ФАКТА =====
    elif message.text == "👀 Интересный факт":

        madrid_facts = SPAIN_FACTS.get("Real Madrid")

        if madrid_facts:
            fact = random.choice(madrid_facts)
            bot.send_message(message.chat.id, fact)
        else:
            bot.send_message(message.chat.id, "Факты не найдены 😢")

# ===============================
# ЗАПУСК БОТА
# ===============================
bot.infinity_polling()
