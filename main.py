import random
import telebot
from telebot import types
from dotenv import dotenv_values

config = dotenv_values(".env")
BOT_TOKEN = config.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Храним состояние: {chat_id: {"league": ..., "club": ...}}
user_state = {}

def load_facts(filename):
    facts_dict = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                if "|" in line:
                    club, facts = line.strip().split("|")
                    facts_dict[club] = [f.strip() for f in facts.split(";")]
    except FileNotFoundError:
        print(f"Предупреждение: Файл {filename} не найден!")
    return facts_dict

ALL_FACTS = {
    "Spain": load_facts("Spain.txt"),
    "England": load_facts("England.txt"),
    "Italy": load_facts("Italy.txt")
}
LEAGUES = ["England", "Spain", "Italy"]
SLOGANS = {
    "Juventus": "All the way to the top!",
    "AC Milan": "Milan, Milan, we are the best!",
    "Barcelona": "Visca el Barça i Visca Catalunya!",
    "Real Madrid": "Hala Madrid!",
    "Liverpool": "You'll Never Walk Alone!",
    "Arsenal": "Come On You Gunners!"
}

def country_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🇬🇧 England", callback_data="England"),
        types.InlineKeyboardButton("🇪🇸 Spain", callback_data="Spain"),
        types.InlineKeyboardButton("🇮🇹 Italy", callback_data="Italy")
    )
    return markup

def club_menu(league):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if league == "England":
        markup.add(types.InlineKeyboardButton("🇬🇧 Liverpool", callback_data="Liverpool"),
                   types.InlineKeyboardButton("🇬🇧 Arsenal", callback_data="Arsenal"))
    elif league == "Spain":
        markup.add(types.InlineKeyboardButton("🇪🇸 Barcelona", callback_data="Barcelona"),
                   types.InlineKeyboardButton("🇪🇸 Real Madrid", callback_data="Real Madrid"))
    elif league == "Italy":
        markup.add(types.InlineKeyboardButton("🇮🇹 Juventus", callback_data="Juventus"),
                   types.InlineKeyboardButton("🇮🇹 AC Milan", callback_data="AC Milan"))
    markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_leagues"))
    return markup

def fact_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("👀 Интересный факт", callback_data="get_fact"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back_to_clubs")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_state[message.chat.id] = {}
    bot.send_message(
        message.chat.id,
        "Давай выберем лигу:",
        reply_markup=country_menu()
    )

@bot.message_handler(commands=['site'])
def site_command(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Открыть сайт с матчами ЧМ-2026', url='https://www.flashscorekz.com/football/world/world-championship/'))
    bot.send_message(message.chat.id, "Кликни по кнопке ниже, чтобы перейти на сайт:", reply_markup=markup)

# --- ОБРАБОТКА НАЖАТИЙ НА INLINE-КНОПКИ ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if data in LEAGUES:
        user_state[chat_id] = {"league": data}
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Отлично, теперь выбери клуб:",
            reply_markup=club_menu(data)
        )

    elif data in SLOGANS:
        user_state[chat_id]["club"] = data
        slogan = SLOGANS[data]
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"{slogan}\nЧто хочешь узнать?",
            reply_markup=fact_menu()
        )

    elif data == "get_fact":
        league = user_state.get(chat_id, {}).get("league")
        club = user_state.get(chat_id, {}).get("club")
        if not league or not club:
            bot.answer_callback_query(call.id, "Сначала выбери клуб! ⚽", show_alert=True)
            return
        facts = ALL_FACTS.get(league, {}).get(club)
        fact_text = random.choice(facts) if facts else "Факты не найдены 😢"
        slogan = SLOGANS.get(club, "")
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"{slogan}\n\n📌 {fact_text}\n\nЧто еще хочешь узнать?",
            reply_markup=fact_menu()
        )

    elif data == "back_to_leagues":
        user_state[chat_id] = {}
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Давай выберем лигу:",
            reply_markup=country_menu()
        )

    elif data == "back_to_clubs":
        league = user_state.get(chat_id, {}).get("league")
        if "club" in user_state.get(chat_id, {}):
            user_state[chat_id].pop("club")
        if league:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Выбери клуб:",
                reply_markup=club_menu(league)
            )
        else:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="Давай выберем лигу:",
                reply_markup=country_menu()
            )

    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.lower() == 'id':
        bot.reply_to(message, f'ID: {message.from_user.id}')

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
