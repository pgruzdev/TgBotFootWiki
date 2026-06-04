import os
import random
import telebot
from telebot import types
import webbrowser
from dotenv import load_dotenv

# Загружаем переменные из файла .env в систему
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ПАМЯТЬ ПОЛЬЗОВАТЕЛЯ
user_state = {}

# ЗАГРУЗКА ФАКТОВ
def load_facts(filename):
    facts_dict = {}
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            club, facts = line.strip().split("|")
            facts_dict[club] = [f.strip() for f in facts.split(";")]
    return facts_dict

SPAIN_FACTS = load_facts("Spain.txt")
ENGLAND_FACTS = load_facts("England.txt")

ALL_FACTS = { "Spain": SPAIN_FACTS, "England": ENGLAND_FACTS}

# КНОПКИ

def country_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 England", "🇪🇸 Spain")
    return markup

def england_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 Liverpool", "🇬🇧 Arsenal")
    markup.add("⬅ Назад")
    return markup

def spain_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇪🇸 Barcelona", "🇪🇸 Real Madrid")
    markup.add("⬅ Назад")
    return markup

def fact_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👀 Интересный факт")
    markup.add("⬅ Назад")
    return markup

# START

@bot.message_handler(commands=['start'])
def start(message):
    user_state[message.chat.id] = {}
    bot.send_message(message.chat.id,"Давай выберем лигу:", reply_markup=country_menu())

# ОБРАБОТЧИК ТЕКСТА

@bot.message_handler(content_types=['text'])
def handle(message):
    chat_id = message.chat.id
    text = message.text

    # НАЗАД

    if text == "⬅ Назад":
        if chat_id not in user_state or "league" not in user_state[chat_id]:
            bot.send_message(chat_id, "Давай выберем лигу:", reply_markup=country_menu())
            return
        # Если был выбран клуб -> возвращаемся к выбору клуба
        if "club" in user_state[chat_id]:
            league = user_state[chat_id]["league"]
            user_state[chat_id].pop("club")
            if league == "Spain":
                bot.send_message(chat_id, "Выбери клуб:", reply_markup=spain_menu())
            else:
                bot.send_message(chat_id, "Выбери клуб:", reply_markup=england_menu())
        # Если была выбрана только страна -> возвращаем к странам
        else:
            user_state[chat_id] = {}
            bot.send_message(chat_id, "Давай выберем лигу:", reply_markup=country_menu())
        return

    # ВЫБОР СТРАНЫ
    if text == "🇪🇸 Spain":
        user_state[chat_id] = {"league": "Spain"}
        bot.send_message(chat_id, "Отлично, теперь выбери клуб", reply_markup=spain_menu())
        return
    if text == "🇬🇧 England":
        user_state[chat_id] = {"league": "England"}
        bot.send_message(chat_id, "Отлично, теперь выбери клуб", reply_markup=england_menu())
        return
    # ВЫБОР КЛУБОВ
    if text == "🇪🇸 Barcelona":
        user_state[chat_id]["club"] = "Barcelona"
        bot.send_message(
            chat_id,
            "Visca el Barça i Visca Catalunya!\nЧто хочешь узнать?",reply_markup=fact_menu())
        return
    if text == "🇪🇸 Real Madrid":
        user_state[chat_id]["club"] = "Real Madrid"
        bot.send_message(chat_id,"Hala Madrid!\nЧто хочешь узнать?",reply_markup=fact_menu())
        return
    if text == "🇬🇧 Liverpool":
        user_state[chat_id]["club"] = "Liverpool"
        bot.send_message(chat_id,"You'll Never Walk Alone!\nЧто хочешь узнать?", reply_markup=fact_menu())
        return
    if text == "🇬🇧 Arsenal":
        user_state[chat_id]["club"] = "Arsenal"
        bot.send_message(chat_id,"Come On You Gunners!\nЧто хочешь узнать?",reply_markup=fact_menu())
        return

    # ИНТЕРЕСНЫЙ ФАКТ
    if text == "👀 Интересный факт":
        if chat_id not in user_state:
            bot.send_message(chat_id, "Сначала выбери страну и клуб ⚽")
            return
        league = user_state[chat_id].get("league")
        club = user_state[chat_id].get("club")
        if not league or not club:
            bot.send_message(chat_id, "Сначала выбери клуб ⚽")
            return
        facts = ALL_FACTS[league].get(club)
        if facts:
            bot.send_message(chat_id, random.choice(facts))
        else:
            bot.send_message(chat_id, "Факты не найдены 😢")
bot.infinity_polling()
