import os
import random
import webbrowser
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ИЗМЕНЕНИЕ: Создан единый словарь конфигурации. Вместо разрозненных IF-условий 
# под каждый клуб, теперь все девизы и флаги лежат в структуре данных.
# Это позволяет добавлять новые лиги и клубы без написания нового кода.
CLUBS_DATA = {
    "Spain": {
        "Barcelona": {"flag": "🇪🇸", "slogan": "Visca el Barça i Visca Catalunya!\nЧто хочешь узнать?"},
        "Real Madrid": {"flag": "🇪🇸", "slogan": "Hala Madrid!\nЧто хочешь узнать?"}
    },
    "England": {
        "Liverpool": {"flag": "🇬🇧", "slogan": "You'll Never Walk Alone!\nЧто хочешь узнать?"},
        "Arsenal": {"flag": "🇬🇧", "slogan": "Come On You Gunners!\nЧто хочешь узнать?"}
    }
}

user_state = {}

def load_facts(filename):
    facts_dict = {}
    if not os.path.exists(filename):
        return facts_dict
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip() or "|" not in line:
                continue
            club, facts = line.strip().split("|")
            facts_dict[club] = [f.strip() for f in facts.split(";")]
    return facts_dict

ALL_FACTS = {
    "Spain": load_facts("Spain.txt"),
    "England": load_facts("England.txt")
}

def country_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇬🇧 England", "🇪🇸 Spain")
    return markup

# ИЗМЕНЕНИЕ: Функции england_menu() и spain_menu() объединены в одну универсальную.
# Она динамически берет ключи клубов из словаря CLUBS_DATA для выбранной лиги
# и сама собирает нужные кнопки с правильными флагами.
def league_menu(league_name):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    clubs = CLUBS_DATA.get(league_name, {})
    for club, info in clubs.items():
        markup.add(f"{info['flag']} {club}")
    markup.add("⬅ Назад")
    return markup

def fact_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👀 Интересный факт")
    markup.add("⬅ Назад")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_state[message.chat.id] = {}
    bot.send_message(message.chat.id, "Давай выберем лигу:", reply_markup=country_menu())

@bot.message_handler(content_types=['text'])
def handle(message):
    chat_id = message.chat.id
    text = message.text

    if text == "⬅ Назад":
        if chat_id not in user_state or "league" not in user_state[chat_id]:
            bot.send_message(chat_id, "Давай выберем лигу:", reply_markup=country_menu())
            return
        
        if "club" in user_state[chat_id]:
            league = user_state[chat_id]["league"]
            user_state[chat_id].pop("club")
            # ИЗМЕНЕНИЕ: Вместо проверки IF для вызова конкретного меню,
            # мы просто передаем текущую лигу в нашу новую универсальную функцию league_menu()
            bot.send_message(chat_id, "Выбери клуб:", reply_markup=league_menu(league))
        else:
            user_state[chat_id] = {}
            bot.send_message(chat_id, "Давай выберем лигу:", reply_markup=country_menu())
        return

    # ИЗМЕНЕНИЕ: Убрали дублирующиеся блоки "if text == '🇪🇸 Spain'" и "if text == '🇬🇧 England'".
    # Теперь мы очищаем текст кнопки от эмодзи флагов и проверяем, есть ли такая страна в CLUBS_DATA.
    clean_country = text.replace("🇬🇧 ", "").replace("🇪🇸 ", "").strip()
    if clean_country in CLUBS_DATA:
        user_state[chat_id] = {"league": clean_country}
        bot.send_message(chat_id, "Отлично, теперь выбери клуб", reply_markup=league_menu(clean_country))
        return

    # ИЗМЕНЕНИЕ: Полностью удалены 4 отдельных блока IF под каждый футбольный клуб.
    # Этот универсальный блок срабатывает, если пользователь уже выбрал лигу, но еще не выбрал клуб.
    # Мы отсекаем эмодзи флага от названия кнопки (например, из '🇪🇸 Barcelona' получаем 'Barcelona')
    # и проверяем, существует ли такой клуб в выбранной лиге. Если да — включаем его девиз.
    if chat_id in user_state and "league" in user_state[chat_id] and "club" not in user_state[chat_id]:
        league = user_state[chat_id]["league"]
        clean_club = text.split(" ", 1)[-1] if " " in text else text
        
        if clean_club in CLUBS_DATA[league]:
            user_state[chat_id]["club"] = clean_club
            slogan = CLUBS_DATA[league][clean_club]["slogan"]
            bot.send_message(chat_id, slogan, reply_markup=fact_menu())
            return

    if text == "👀 Интересный факт":
        if chat_id not in user_state:
            bot.send_message(chat_id, "Сначала выбери страну и клуб ⚽")
            return
        league = user_state[chat_id].get("league")
        club = user_state[chat_id].get("club")
        if not league or not club:
            bot.send_message(chat_id, "Сначала выбери клуб ⚽")
            return
        
        facts = ALL_FACTS.get(league, {}).get(club)
        if facts:
            bot.send_message(chat_id, random.choice(facts))
        else:
            bot.send_message(chat_id, "Факты не найдены 😢")

bot.infinity_polling()
