import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Забираем одну длинную строку подключения из .env
db_url = os.getenv("DATABASE_URL")

try:
    # Передаем строку прямо в коннектор
    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()
    
    # Делаем проверочный запрос к твоей таблице leagues
    cursor.execute("SELECT name_ru, flag FROM leagues;")
    leagues = cursor.fetchall()
    
    print("✅ Успешное подключение к Supabase через DATABASE_URL!")
    print("Список лиг в базе:")
    for league in leagues:
        print(f"{league[1]} {league[0]}")
        
    cursor.close()
    connection.close()

except Exception as error:
    print("❌ Ошибка при подключении к базе данных:")
    print(error)
