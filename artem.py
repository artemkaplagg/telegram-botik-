import telebot
from telebot import types
import json
import os
import datetime
import time
import threading
from collections import defaultdict
import random
import requests
import schedule
import emoji
import qrcode
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import hashlib
import re
from dateutil import parser
from bs4 import BeautifulSoup

# ==================== КОНФИГУРАЦИЯ ====================
BOT_TOKEN = "8372710595:AAF5VKiSbHbOYmTitWfyohrtHQ1OIEI44X8"

# ID администраторов - исправлено согласно данным
OWNER_ID = 6185367393  # Твой ID (владелец)
ADMIN_ID = 6738617654  # ID Насти (староста)

# ID учеников 1 группы - обновленный список
GROUP_1_IDS = [
    6185367393, 5650809687, 5566682926, 5029724753, 6738617654,
    5379148476, 1942365829, 8481372472, 860000457, 5241074325,
    1312687739, 1236979350, 995840535, 1240354802, 6558632830
]

# Расписание звонков
BELL_SCHEDULE = {
    1: "08:30 - 09:15",
    2: "09:25 - 10:10", 
    3: "10:20 - 11:05",
    4: "11:35 - 12:20",
    5: "12:30 - 13:15",
    6: "13:25 - 14:10",
    7: "14:20 - 15:05",
    8: "15:15 - 16:00"
}

# Расписание уроков для групп
SCHEDULE = {
    "Понедельник": {
        "group1": [
            {"subject": "Мистецтво", "room": "206", "teacher": "Сорочан Н.Є."},
            {"subject": "Биология", "room": "569", "teacher": "Лавок О.М."},
            {"subject": "Здоровье", "room": "248", "teacher": "Марченко Ю.О."},
            {"subject": "Всемирная история", "room": "203", "teacher": "Загребельна Л.П."},
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І.", "group_note": "1 группа"},
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "2 группа"},
            {"subject": "Информатика", "room": "407", "teacher": "Бабаєвський Олександр", "group_note": "2 группа"}
        ],
        "group2": [
            {"subject": "Мистецтво", "room": "206", "teacher": "Сорочан Н.Є."},
            {"subject": "Биология", "room": "569", "teacher": "Лавок О.М."},
            {"subject": "Здоровье", "room": "248", "teacher": "Марченко Ю.О."},
            {"subject": "Всемирная история", "room": "203", "teacher": "Загребельна Л.П."},
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "2 группа"},
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І.", "group_note": "1 группа"},
            {"subject": "Информатика", "room": "407", "teacher": "Бабаєвський Олександр", "group_note": "2 группа"}
        ]
    },
    "Вторник": {
        "group1": [
            {"subject": "Биология", "room": "569", "teacher": "Лавок О.М."},
            {"subject": "Математика", "room": "200", "teacher": "Майдан Віктор Іванівна"},
            {"subject": "Финансовая грамотность", "room": "242", "teacher": "Приходько Л.І."},
            {"subject": "Физическая культура", "room": "610", "teacher": "Ольховик Андрій Дмитрович"},
            {"subject": "Физика", "room": "145", "teacher": "Салівон Н.Г."}
        ],
        "group2": [
            {"subject": "Биология", "room": "569", "teacher": "Лавок О.М."},
            {"subject": "Математика", "room": "200", "teacher": "Майдан Віктор Іванівна"},
            {"subject": "Финансовая грамотность", "room": "242", "teacher": "Приходько Л.І."},
            {"subject": "Физическая культура", "room": "610", "teacher": "Ольховик Андрій Дмитрович"},
            {"subject": "Физика", "room": "145", "teacher": "Салівон Н.Г."}
        ]
    },
    "Среда": {
        "group1": [
            {"subject": "Информатика", "room": "407", "teacher": "Бабаєвський Олександр", "group_note": "1 группа"},
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І.", "group_note": "2 группа"},
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І.", "group_note": "1 группа"},
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "2 группа"},
            {"subject": "Физическая культура", "room": "610", "teacher": "Ольховик Андрій Дмитрович"},
            {"subject": "Химия", "room": "428", "teacher": "Селезньова Ю.О."},
            {"subject": "Технологии", "room": "502", "teacher": "Григорьева", "group_note": "1 группа"}
        ],
        "group2": [
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І.", "group_note": "2 группа"},
            {"subject": "Информатика", "room": "407", "teacher": "Бабаєвський Олександр", "group_note": "1 группа"},
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "2 группа"},
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І.", "group_note": "1 группа"},
            {"subject": "Физическая культура", "room": "610", "teacher": "Ольховик Андрій Дмитрович"},
            {"subject": "Химия", "room": "428", "teacher": "Селезньова Ю.О."},
            {"subject": "Технологии", "room": "502", "teacher": "Григорьева", "group_note": "1 группа"}
        ]
    },
    "Четверг": {
        "group1": [
            {"subject": "История Украины", "room": "203", "teacher": "Загребельна Л.П."},
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "1 группа"},
            {"subject": "Технологии", "room": "502", "teacher": "Григорьева", "group_note": "2 группа"},
            {"subject": "Зарубежная литература", "room": "242", "teacher": "Приходько Л.І."},
            {"subject": "Математика", "room": "200", "teacher": "Майдан Віктор Іванівна"},
            {"subject": "Украинская литература", "room": "335", "teacher": "Буяльська Н.І."},
            {"subject": "Физическая культура", "room": "610", "teacher": "Ольховик Андрій Дмитрович"}
        ],
        "group2": [
            {"subject": "История Украины", "room": "203", "teacher": "Загребельна Л.П."},
            {"subject": "Технологии", "room": "502", "teacher": "Григорьева", "group_note": "2 группа"},
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "1 группа"},
            {"subject": "Зарубежная литература", "room": "242", "teacher": "Приходько Л.І."},
            {"subject": "Математика", "room": "200", "teacher": "Майдан Віктор Іванівна"},
            {"subject": "Украинская литература", "room": "335", "teacher": "Буяльська Н.І."},
            {"subject": "Физическая культура", "room": "610", "teacher": "Ольховик Андрій Дмитрович"}
        ]
    },
    "Пятница": {
        "group1": [
            {"subject": "STEM", "room": "408", "teacher": "Борецький К.П.", "group_note": "1 группа"},
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "2 группа"},
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І."},
            {"subject": "Математика", "room": "200", "teacher": "Майдан Віктор Іванівна"},
            {"subject": "Украинская литература", "room": "335", "teacher": "Буяльська Н.І."},
            {"subject": "География", "room": "592", "teacher": "Бабеща С.В."}
        ],
        "group2": [
            {"subject": "Украинский язык", "room": "335", "teacher": "Буяльська Н.І.", "group_note": "2 группа"},
            {"subject": "STEM", "room": "408", "teacher": "Борецький К.П.", "group_note": "1 группа"},
            {"subject": "Английский язык", "room": "410", "teacher": "Глибко С.І."},
            {"subject": "Математика", "room": "200", "teacher": "Майдан Віктор Іванівна"},
            {"subject": "Украинская литература", "room": "335", "teacher": "Буяльська Н.І."},
            {"subject": "География", "room": "592", "teacher": "Бабеща С.В."}
        ]
    }
}

# Файлы для хранения данных
DATA_DIR = "bot_data"
USERS_FILE = f"{DATA_DIR}/users.json"
HOMEWORK_FILE = f"{DATA_DIR}/homework.json"
MESSAGES_FILE = f"{DATA_DIR}/messages.json"
SETTINGS_FILE = f"{DATA_DIR}/settings.json"
STATS_FILE = f"{DATA_DIR}/stats.json"
DUTY_FILE = f"{DATA_DIR}/duty.json"
GRADES_FILE = f"{DATA_DIR}/grades.json"
TESTS_FILE = f"{DATA_DIR}/tests.json"
EVENTS_FILE = f"{DATA_DIR}/events.json"
ATTENDANCE_FILE = f"{DATA_DIR}/attendance.json"
FEEDBACK_FILE = f"{DATA_DIR}/feedback.json"
POLLS_FILE = f"{DATA_DIR}/polls.json"
QUOTES_FILE = f"{DATA_DIR}/quotes.json"
NOTES_FILE = f"{DATA_DIR}/notes.json"
REMINDERS_FILE = f"{DATA_DIR}/reminders.json"

# Создаем директорию для данных
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Создаем папку для изображений
IMAGES_DIR = f"{DATA_DIR}/images"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# ==================== ФУНКЦИИ РАБОТЫ С ДАННЫМИ ====================

def load_data(filename, default={}):
    """Загружает данные из JSON файла"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки {filename}: {e}")
    return default

def save_data(filename, data):
    """Сохраняет данные в JSON файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения {filename}: {e}")
        return False

# Загрузка всех данных
users = load_data(USERS_FILE, {})
homework = load_data(HOMEWORK_FILE, {})
important_messages = load_data(MESSAGES_FILE, [])
settings = load_data(SETTINGS_FILE, {"notifications": True, "reminders": True})
stats = load_data(STATS_FILE, {"commands": {}, "daily_active": {}})
duty_schedule = load_data(DUTY_FILE, {"current_week": 1, "schedule": {}})
grades = load_data(GRADES_FILE, {})
tests = load_data(TESTS_FILE, {})
events = load_data(EVENTS_FILE, [])
attendance = load_data(ATTENDANCE_FILE, {})
feedback = load_data(FEEDBACK_FILE, [])
polls = load_data(POLLS_FILE, {})
quotes = load_data(QUOTES_FILE, [])
notes = load_data(NOTES_FILE, {})
reminders = load_data(REMINDERS_FILE, {})

# ==================== ФУНКЦИИ АВТОРИЗАЦИИ И ПРОВЕРОК ====================

def is_authorized(user_id):
    """Проверяет авторизацию пользователя"""
    return str(user_id) in users or user_id in GROUP_1_IDS

def is_owner(user_id):
    """Проверяет владельца бота"""
    return user_id == OWNER_ID

def is_admin(user_id):
    """Проверяет админа (староста + владелец)"""
    return user_id == ADMIN_ID or user_id == OWNER_ID

def get_user_group(user_id):
    """Определяет группу пользователя"""
    user_data = users.get(str(user_id), {})
    return user_data.get('group', 1)  # По умолчанию 1 группа

def log_command(user_id, command):
    """Логирует использование команды"""
    today = datetime.date.today().isoformat()
    
    # Статистика команд
    if command not in stats["commands"]:
        stats["commands"][command] = 0
    stats["commands"][command] += 1
    
    # Ежедневная активность
    if today not in stats["daily_active"]:
        stats["daily_active"][today] = []
    
    if user_id not in stats["daily_active"][today]:
        stats["daily_active"][today].append(user_id)
    
    save_data(STATS_FILE, stats)

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_current_day():
    """Возвращает текущий день недели по-русски"""
    days = {
        0: "Понедельник", 1: "Вторник", 2: "Среда", 
        3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
    }
    return days.get(datetime.datetime.now().weekday(), "Понедельник")

def get_tomorrow_day():
    """Возвращает завтрашний день недели по-русски"""
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    days = {
        0: "Понедельник", 1: "Вторник", 2: "Среда", 
        3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
    }
    return days.get(tomorrow.weekday(), "Понедельник")

def get_current_lesson():
    """Определяет текущий урок"""
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    
    for lesson_num, time_range in BELL_SCHEDULE.items():
        start_time, end_time = time_range.split(" - ")
        if start_time <= current_time <= end_time:
            return f"{lesson_num} урок ({time_range})"
    
    return None

def get_username_by_id(user_id):
    """Получить username по ID"""
    user_data = users.get(str(user_id), {})
    return user_data.get('username', 'Неизвестный')

def get_first_name_by_id(user_id):
    """Получить имя по ID"""
    user_data = users.get(str(user_id), {})
    return user_data.get('first_name', 'Неизвестный')

def generate_qr_code(text):
    """Генерация QR кода"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

def create_attendance_chart():
    """Создание графика посещаемости"""
    try:
        dates = list(attendance.keys())[-7:]  # Последние 7 дней
        present_counts = []
        absent_counts = []
        
        for date in dates:
            day_data = attendance.get(date, {})
            present = len([s for s in day_data.values() if s == 'present'])
            absent = len([s for s in day_data.values() if s == 'absent'])
            present_counts.append(present)
            absent_counts.append(absent)
        
        plt.figure(figsize=(10, 6))
        plt.bar(dates, present_counts, label='Присутствуют', color='green', alpha=0.7)
        plt.bar(dates, absent_counts, bottom=present_counts, label='Отсутствуют', color='red', alpha=0.7)
        
        plt.title('Посещаемость за последние 7 дней')
        plt.xlabel('Дата')
        plt.ylabel('Количество учеников')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = f"{IMAGES_DIR}/attendance_chart.png"
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    except Exception as e:
        print(f"Ошибка создания графика: {e}")
        return None

def create_grades_chart(user_id):
    """Создание графика оценок ученика"""
    try:
        user_grades = grades.get(str(user_id), {})
        if not user_grades:
            return None
        
        subjects = list(user_grades.keys())
        avg_grades = []
        
        for subject in subjects:
            subject_grades = user_grades[subject]
            if subject_grades:
                avg_grade = sum(subject_grades) / len(subject_grades)
                avg_grades.append(avg_grade)
            else:
                avg_grades.append(0)
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(subjects, avg_grades, color=['skyblue', 'lightgreen', 'lightcoral', 'gold', 'plum'])
        
        plt.title(f'Средние оценки - {get_first_name_by_id(user_id)}')
        plt.xlabel('Предметы')
        plt.ylabel('Средняя оценка')
        plt.ylim(0, 12)
        
        # Добавляем значения на столбцы
        for bar, grade in zip(bars, avg_grades):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{grade:.1f}', ha='center', va='bottom')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = f"{IMAGES_DIR}/grades_{user_id}.png"
        plt.savefig(chart_path)
        plt.close()
        
        return chart_path
    except Exception as e:
        print(f"Ошибка создания графика оценок: {e}")
        return None

def get_weather():
    """Получение погоды (заглушка)"""
    weather_options = [
        "☀️ Солнечно, +18°C",
        "🌤️ Переменная облачность, +15°C", 
        "🌧️ Дождь, +12°C",
        "❄️ Снег, -2°C",
        "🌫️ Туман, +8°C"
    ]
    return random.choice(weather_options)

def get_random_fact():
    """Случайный интересный факт"""
    facts = [
        "🧠 Человеческий мозг потребляет около 20% всей энергии тела",
        "🐙 У осьминога три сердца",
        "🌍 Земля вращается со скоростью 1600 км/ч на экваторе",
        "🍯 Мед никогда не портится",
        "🦈 Акулы существуют дольше деревьев",
        "🌙 Луна удаляется от Земли на 3.8 см каждый год",
        "🐧 Пингвины могут подпрыгивать на высоту до 2 метров",
        "🧊 Горячая вода замерзает быстрее холодной"
    ]
    return random.choice(facts)

def get_motivational_quote():
    """Мотивационная цитата"""
    motivational_quotes = [
        "💪 Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма",
        "🎯 Мечты сбываются у тех, кто просыпается и идет к ним навстречу",
        "🚀 Не ждите идеального момента. Начните прямо сейчас",
        "⭐ Вы сильнее, чем думаете",
        "🌟 Каждый день - новая возможность стать лучше",
        "🏆 Трудности делают нас сильнее",
        "🔥 Верь в себя и все получится"
    ]
    return random.choice(motivational_quotes)

# ==================== ФУНКЦИИ КЛАВИАТУР ====================

def main_menu():
    """Главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📅 Расписание", "📚 Домашние задания",
        "📢 Объявления", "🔔 Звонки", 
        "👥 Дежурство", "📊 Мои оценки",
        "📈 Статистика", "🎯 Тесты и опросы",
        "📝 Заметки", "🎲 Развлечения",
        "⚙️ Настройки", "ℹ️ Помощь"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    
    # Добавляем кнопки поддержки внизу
    support_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    support_markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    
    return markup

def schedule_menu():
    """Меню расписания"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    days = ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница"]
    for day in days:
        markup.add(types.KeyboardButton(day))
    
    markup.add(
        types.KeyboardButton("📅 Сегодня"),
        types.KeyboardButton("📅 Завтра")
    )
    markup.add(
        types.KeyboardButton("📊 Полное расписание"),
        types.KeyboardButton("🎨 Расписание-картинка")
    )
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

def homework_menu():
    """Меню домашних заданий"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📝 Все ДЗ", "📝 На завтра",
        "📝 На неделю", "📝 Мои предметы",
        "📊 Статистика ДЗ", "🔍 Поиск ДЗ"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

def admin_menu():
    """Админское меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "👑 Управление ДЗ", "📢 Отправить объявление",
        "👥 Управление дежурством", "📊 Статистика админа",
        "📈 Управление оценками", "📋 Посещаемость",
        "🎯 Создать тест", "📅 Управление событиями",
        "⚙️ Настройки бота", "👤 Список учеников"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

def homework_admin_menu():
    """Админское меню ДЗ"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "➕ Добавить ДЗ", "📋 Список всех ДЗ",
        "❌ Удалить ДЗ", "📝 Редактировать ДЗ",
        "📤 Экспорт ДЗ", "📥 Импорт ДЗ"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

def entertainment_menu():
    """Меню развлечений"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "🎲 Случайное число", "🎭 Анекдот",
        "🧠 Интересный факт", "💪 Мотивация",
        "🎵 Цитата дня", "🌤️ Погода",
        "🎯 Викторина", "🎪 Игры"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

def grades_menu():
    """Меню оценок"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📊 Мои оценки", "📈 График оценок",
        "📋 По предметам", "🏆 Средний балл",
        "📅 За период", "📊 Сравнение с классом"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

def support_menu():
    """Меню поддержки"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton(f"👑 Написать владельцу @{get_username_by_id(OWNER_ID)}"),
        types.KeyboardButton(f"👨‍💼 Написать старосте @{get_username_by_id(ADMIN_ID)}"),
        types.KeyboardButton("🔙 Главное меню")
    )
    return markup

def back_keyboard():
    """Кнопка назад и поддержки"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

# ==================== ОБРАБОТЧИКИ КОМАНД ====================

@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    first_name = message.from_user.first_name or ""
    
    log_command(user_id, "start")
    
    if user_id in GROUP_1_IDS:
        # Автоматическая регистрация для учеников из списка
        if str(user_id) not in users:
            users[str(user_id)] = {
                'username': username,
                'first_name': first_name,
                'group': 1,  # Пока все в 1 группе
                'registered': datetime.datetime.now().isoformat(),
                'role': 'admin' if user_id == ADMIN_ID else 'owner' if user_id == OWNER_ID else 'student',
                'last_activity': datetime.datetime.now().isoformat(),
                'total_commands': 0,
                'favorite_subjects': [],
                'notifications_enabled': True
            }
            save_data(USERS_FILE, users)
            
            # Сообщение с благодарностью для новых пользователей
            welcome_text = f"""
🎉 Добро пожаловать в супер-бот 8-А класса!

✅ Привет, {first_name}! (@{username}) 
🎊 Ты успешно зарегистрирован в самом крутом школьном боте!

👥 Группа: 1
📋 Статус: {'👑 Владелец' if user_id == OWNER_ID else '👨‍💼 Староста' if user_id == ADMIN_ID else '👤 Ученик'}

🙏 СКАЖИТЕ СПАСИБО АРТЕМУ И НАСТЕ ЗА РАБОТУ С БОТОМ!

🏫 Киевская инженерная гимназия
🚀 Теперь ты можешь:
• 📅 Смотреть расписание уроков на любой день
• 📚 Получать актуальные домашние задания
• 📢 Читать важные объявления от старосты
• 👥 Узнавать график дежурств
• 📊 Отслеживать свои оценки и статистику
• 🎯 Участвовать в тестах и опросах
• 📝 Делать заметки и напоминания
• 🎲 Развлекаться в свободное время
• 🌤️ Узнавать погоду и интересные факты
• 💬 Получать поддержку от администраторов
• И многое другое!

🌟 Выбери нужный раздел в меню ⬇️
            """
        else:
            # Обновляем активность
            users[str(user_id)]['last_activity'] = datetime.datetime.now().isoformat()
            users[str(user_id)]['total_commands'] = users[str(user_id)].get('total_commands', 0) + 1
            save_data(USERS_FILE, users)
            
            user_data = users[str(user_id)]
            role_text = "👑 Владелец" if user_id == OWNER_ID else "👨‍💼 Староста" if user_id == ADMIN_ID else "👤 Ученик"
            
            welcome_text = f"""
🎓 С возвращением в супер-бот 8-А класса!

👋 Привет, {first_name}! (@{username})
📋 Статус: {role_text}
👥 Группа: {user_data['group']}
📈 Команд использовано: {user_data.get('total_commands', 0)}

🙏 СКАЖИТЕ СПАСИБО АРТЕМУ И НАСТЕ ЗА РАБОТУ С БОТОМ!

🏫 Киевская инженерная гимназия
🚀 Здесь ты можешь:
• 📅 Смотреть расписание уроков  
• 📚 Получать домашние задания  
• 📢 Читать объявления от старосты
• 👥 Узнавать график дежурств
• 📊 Следить за оценками и статистикой класса
• 🎯 Участвовать в тестах и викторинах
• 📝 Управлять заметками и напоминаниями
• 🎲 Развлекаться и узнавать новое
• 💬 Получать помощь от админов
• И многое другое!

🌟 Выбери нужный раздел в меню ⬇️
            """
        
        bot.send_message(
            message.chat.id,
            welcome_text.strip(),
            reply_markup=main_menu()
        )
    else:
        # Неавторизованный пользователь
        bot.send_message(
            message.chat.id,
            f"""
❌ Доступ ограничен!

Этот супер-бот предназначен только для учеников 8-А класса 
Киевской инженерной гимназии.

Если ты ученик нашего класса, обратись к Артему (владельцу) или Насте (старосте) для добавления в бот.

👨‍💻 Владелец: @{get_username_by_id(OWNER_ID)}
👨‍💼 Староста: @{get_username_by_id(ADMIN_ID)}

Твой ID: {user_id}

💬 Если возникли вопросы, напиши в поддержку!
            """,
            reply_markup=support_menu()
        )

@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Админская панель"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав администратора!")
        return
    
    log_command(user_id, "admin")
    
    admin_text = f"""
👑 Панель супер-администратора

Добро пожаловать, {'владелец' if is_owner(user_id) else 'староста'}!

📊 Быстрая статистика:
• Зарегистрировано учеников: {len([u for u in users.values() if u.get('role') == 'student'])}
• Домашних заданий: {len(homework)}
• Объявлений: {len(important_messages)}
• Активных сегодня: {len(stats.get('daily_active', {}).get(datetime.date.today().isoformat(), []))}
• Оценок в системе: {sum(len(g) for g in grades.values() for g in g.values())}
• Тестов создано: {len(tests)}
• Событий запланировано: {len(events)}

🚀 Выберите действие:
    """
    
    bot.send_message(
        message.chat.id,
        admin_text.strip(),
        reply_markup=admin_menu()
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    """Справка по боту"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "help")
    show_help(message)

@bot.message_handler(commands=['stats'])
def quick_stats_command(message):
    """Быстрая статистика"""
    if not is_authorized(message.from_user.id):
        return
    
    user_id = message.from_user.id
    log_command(user_id, "stats")
    
    today = datetime.date.today().isoformat()
    user_data = users.get(str(user_id), {})
    
    stats_text = f"📊 Твоя статистика:\n\n"
    stats_text += f"📅 Зарегистрирован: {user_data.get('registered', 'Неизвестно')[:10]}\n"
    stats_text += f"📈 Команд использовано: {user_data.get('total_commands', 0)}\n"
    stats_text += f"📚 Любимые предметы: {', '.join(user_data.get('favorite_subjects', [])) or 'Не выбраны'}\n"
    
    user_grades = grades.get(str(user_id), {})
    if user_grades:
        total_grades = sum(len(subject_grades) for subject_grades in user_grades.values())
        avg_grade = sum(sum(subject_grades) for subject_grades in user_grades.values()) / total_grades if total_grades > 0 else 0
        stats_text += f"📊 Всего оценок: {total_grades}\n"
        stats_text += f"🏆 Средний балл: {avg_grade:.2f}\n"
    
    bot.send_message(message.chat.id, stats_text, reply_markup=back_keyboard())

# ==================== ОБРАБОТЧИКИ ОСНОВНОГО МЕНЮ ====================

@bot.message_handler(func=lambda message: message.text == "📅 Расписание")
def schedule_handler(message):
    """Обработчик расписания"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "schedule")
    
    bot.send_message(
        message.chat.id,
        "📅 Расписание уроков\n\nВыбери день недели или действие:",
        reply_markup=schedule_menu()
    )

@bot.message_handler(func=lambda message: message.text.startswith("📅"))
def day_schedule_handler(message):
    """Обработчик расписания по дням"""
    if not is_authorized(message.from_user.id):
        return
    
    user_id = message.from_user.id
    user_group = get_user_group(user_id)
    
    # Определяем день
    if message.text == "📅 Сегодня":
        day = get_current_day()
    elif message.text == "📅 Завтра":
        day = get_tomorrow_day()
    else:
        day = message.text.replace("📅 ", "")
    
    if day not in SCHEDULE:
        bot.send_message(
            message.chat.id,
            f"❌ Расписание на {day} не найдено!\n\n📅 Доступные дни: Понедельник-Пятница",
            reply_markup=schedule_menu()
        )
        return
    
    # Создаем интерактивное расписание с кнопками для каждого урока
    group_key = f"group{user_group}"
    lessons = SCHEDULE[day][group_key]
    
    schedule_text = f"📅 Расписание на {day}\n"
    schedule_text += f"👥 Группа {user_group}\n"
    schedule_text += f"🌤️ Погода: {get_weather()}\n\n"
    schedule_text += "💡 Нажми на урок чтобы увидеть ДЗ или добавить его!\n\n"
    
    # Создаем кнопки для каждого урока
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    current_lesson = get_current_lesson()
    
    for i, lesson in enumerate(lessons):
        lesson_num = i + 1
        bell_time = BELL_SCHEDULE.get(lesson_num, "")
        
        # Текст для кнопки урока
        if current_lesson and f"{lesson_num} урок" in current_lesson and day == get_current_day():
            lesson_button_text = f"▶️ {lesson_num}. {lesson['subject']} ({bell_time})"
        else:
            lesson_button_text = f"{lesson_num}. {lesson['subject']} ({bell_time})"
        
        # Добавляем информацию о ДЗ в название кнопки
        hw_key = f"{day}_{lesson['subject']}"
        if hw_key in homework:
            lesson_button_text += " 📝"
        
        markup.add(types.KeyboardButton(f"📚 {day}|{lesson['subject']}"))
        
        # Добавляем в текст основную информацию
        if current_lesson and f"{lesson_num} урок" in current_lesson and day == get_current_day():
            schedule_text += f"▶️ {lesson_num}. "
        else:
            schedule_text += f"{lesson_num}. "
        
        schedule_text += f"📚 {lesson['subject']}\n"
        schedule_text += f"   🏫 Кабинет {lesson['room']}\n"
        schedule_text += f"   👨‍🏫 {lesson['teacher']}\n"
        schedule_text += f"   🕐 {bell_time}\n"
        
        if lesson.get('group_note'):
            schedule_text += f"   👥 {lesson['group_note']}\n"
        
        schedule_text += "\n"
    
    if current_lesson and day == get_current_day():
        schedule_text += f"🔔 Сейчас: {current_lesson}\n\n"
    
    # Добавляем кнопки навигации
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    
    bot.send_message(
        message.chat.id,
        schedule_text,
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "📊 Полное расписание")
def full_schedule_handler(message):
    """Полное расписание на неделю"""
    if not is_authorized(message.from_user.id):
        return
    
    user_group = get_user_group(message.from_user.id)
    
    schedule_text = f"📊 Полное расписание - Группа {user_group}\n\n"
    
    for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]:
        schedule_text += f"📅 {day}:\n"
        lessons = SCHEDULE[day][f"group{user_group}"]
        
        for i, lesson in enumerate(lessons, 1):
            schedule_text += f"  {i}. {lesson['subject']} ({lesson['room']})\n"
        
        schedule_text += "\n"
    
    bot.send_message(message.chat.id, schedule_text, reply_markup=schedule_menu())

@bot.message_handler(func=lambda message: message.text == "🎨 Расписание-картинка")
def schedule_image_handler(message):
    """Создание расписания в виде картинки"""
    if not is_authorized(message.from_user.id):
        return
    
    try:
        user_group = get_user_group(message.from_user.id)
        
        # Создаем изображение
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)
        
        # Заголовок
        draw.text((50, 30), f"Расписание 8-А класса (Группа {user_group})", fill='black')
        
        y_pos = 80
        for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]:
            draw.text((50, y_pos), f"{day}:", fill='blue')
            y_pos += 30
            
            lessons = SCHEDULE[day][f"group{user_group}"]
            for i, lesson in enumerate(lessons, 1):
                lesson_text = f"  {i}. {lesson['subject']} (каб. {lesson['room']})"
                draw.text((70, y_pos), lesson_text, fill='black')
                y_pos += 25
            
            y_pos += 20
        
        # Сохраняем изображение
        image_path = f"{IMAGES_DIR}/schedule_{user_group}.png"
        img.save(image_path)
        
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, 
                          caption=f"📅 Расписание для группы {user_group}",
                          reply_markup=schedule_menu())
    
    except Exception as e:
        bot.send_message(message.chat.id, 
                        f"❌ Ошибка создания картинки: {e}",
                        reply_markup=schedule_menu())

@bot.message_handler(func=lambda message: message.text == "📚 Домашние задания")
def homework_handler(message):
    """Обработчик домашних заданий"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "homework")
    
    bot.send_message(
        message.chat.id,
        "📚 Домашние задания\n\nВыбери опцию:",
        reply_markup=homework_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📝 Все ДЗ")
def all_homework_handler(message):
    """Показать все ДЗ"""
    if not is_authorized(message.from_user.id):
        return
    
    if not homework:
        bot.send_message(
            message.chat.id,
            "📝 Домашних заданий пока нет!\n\n🎉 Можешь отдохнуть!",
            reply_markup=homework_menu()
        )
        return
    
    hw_text = "📚 Все домашние задания:\n\n"
    
    for i, (key, hw_data) in enumerate(homework.items(), 1):
        day, subject = key.split('_', 1) if '_' in key else (key, 'Неизвестный предмет')
        hw_text += f"{i}. 📅 {day} - 📚 {subject}\n"
        hw_text += f"📝 {hw_data['text']}\n"
        hw_text += f"📅 Добавлено: {hw_data.get('date', 'Неизвестно')}\n"
        hw_text += f"👤 Добавил: {hw_data.get('added_by', 'Неизвестно')}\n\n"
    
    hw_text += f"📊 Всего заданий: {len(homework)}"
    
    bot.send_message(message.chat.id, hw_text, reply_markup=homework_menu())

@bot.message_handler(func=lambda message: message.text == "📝 На завтра")
def tomorrow_homework_handler(message):
    """Показать ДЗ на завтра"""
    if not is_authorized(message.from_user.id):
        return
    
    tomorrow = get_tomorrow_day()
    user_group = get_user_group(message.from_user.id)
    
    hw_text = f"📚 Домашние задания на {tomorrow}:\n\n"
    found_hw = False
    
    # Получаем предметы на завтра
    if tomorrow in SCHEDULE:
        lessons = SCHEDULE[tomorrow][f"group{user_group}"]
        for lesson in lessons:
            subject = lesson['subject']
            key = f"{tomorrow}_{subject}"
            
            if key in homework:
                found_hw = True
                hw_data = homework[key]
                hw_text += f"📚 {subject}\n"
                hw_text += f"📝 {hw_data['text']}\n"
                hw_text += f"👤 Добавил: {hw_data.get('added_by', 'Неизвестно')}\n"
                hw_text += f"📅 {hw_data.get('date', 'Неизвестно')}\n\n"
    
    if not found_hw:
        hw_text += "🎉 На завтра домашних заданий нет!\n\n"
        hw_text += f"💡 {get_motivational_quote()}"
    else:
        hw_text += "💪 Удачи с выполнением!"
    
    bot.send_message(message.chat.id, hw_text, reply_markup=homework_menu())

@bot.message_handler(func=lambda message: message.text == "📝 На неделю")
def week_homework_handler(message):
    """ДЗ на всю неделю"""
    if not is_authorized(message.from_user.id):
        return
    
    user_group = get_user_group(message.from_user.id)
    
    hw_text = "📚 Домашние задания на неделю:\n\n"
    total_hw = 0
    
    for day in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]:
        day_hw = []
        if day in SCHEDULE:
            lessons = SCHEDULE[day][f"group{user_group}"]
            for lesson in lessons:
                key = f"{day}_{lesson['subject']}"
                if key in homework:
                    day_hw.append(f"📚 {lesson['subject']}: {homework[key]['text'][:50]}...")
                    total_hw += 1
        
        if day_hw:
            hw_text += f"📅 {day}:\n"
            for hw in day_hw:
                hw_text += f"  {hw}\n"
            hw_text += "\n"
    
    if total_hw == 0:
        hw_text += "🎉 На всю неделю нет домашних заданий!"
    else:
        hw_text += f"📊 Всего заданий на неделю: {total_hw}"
    
    bot.send_message(message.chat.id, hw_text, reply_markup=homework_menu())

@bot.message_handler(func=lambda message: message.text == "🔔 Звонки")
def bells_handler(message):
    """Обработчик расписания звонков"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "bells")
    
    bells_text = "🔔 Расписание звонков:\n\n"
    
    current_lesson = get_current_lesson()
    now = datetime.datetime.now()
    
    for lesson_num, time_range in BELL_SCHEDULE.items():
        if current_lesson and f"{lesson_num} урок" in current_lesson:
            bells_text += f"▶️ {lesson_num} урок: {time_range} 🔔\n"
        else:
            bells_text += f"{lesson_num} урок: {time_range}\n"
    
    if current_lesson:
        bells_text += f"\n🔔 Сейчас: {current_lesson}"
    else:
        bells_text += "\n⏰ Сейчас перемена или учебный день окончен"
    
    # Добавляем время до следующего урока
    next_lesson_time = None
    for lesson_num, time_range in BELL_SCHEDULE.items():
        start_time = time_range.split(" - ")[0]
        lesson_datetime = datetime.datetime.strptime(f"{now.date()} {start_time}", "%Y-%m-%d %H:%M")
        if lesson_datetime > now:
            next_lesson_time = lesson_datetime
            bells_text += f"\n⏳ До {lesson_num} урока: {str(lesson_datetime - now).split('.')[0]}"
            break
    
    bells_text += f"\n\n🌤️ Погода: {get_weather()}"
    
    bot.send_message(message.chat.id, bells_text, reply_markup=back_keyboard())

@bot.message_handler(func=lambda message: message.text == "📢 Объявления")
def announcements_handler(message):
    """Обработчик объявлений"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "announcements")
    
    if not important_messages:
        bot.send_message(
            message.chat.id,
            "📢 Объявлений пока нет!\n\n📱 Следи за обновлениями!",
            reply_markup=back_keyboard()
        )
        return
    
    announcements_text = "📢 Важные объявления:\n\n"
    
    for i, msg in enumerate(reversed(important_messages[-10:]), 1):  # Показываем последние 10
        announcements_text += f"{i}. 📅 {msg.get('date', 'Неизвестно')}\n"
        announcements_text += f"📝 {msg['text']}\n"
        announcements_text += f"👤 От: {msg.get('author', 'Неизвестно')}\n\n"
    
    announcements_text += f"📊 Всего объявлений: {len(important_messages)}"
    
    bot.send_message(message.chat.id, announcements_text, reply_markup=back_keyboard())

@bot.message_handler(func=lambda message: message.text == "👥 Дежурство")
def duty_handler(message):
    """Обработчик дежурства"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "duty")
    
    # Расширенная система дежурства
    current_week = duty_schedule.get("current_week", 1)
    student_list = [uid for uid in users.keys() if users[uid].get('role') == 'student']
    
    if student_list:
        duty_index = (current_week - 1) % len(student_list)
        duty_student_id = student_list[duty_index]
        duty_student = users[duty_student_id]
        
        # Следующий дежурный
        next_duty_index = duty_index + 1 if duty_index + 1 < len(student_list) else 0
        next_duty_student_id = student_list[next_duty_index]
        next_duty_student = users[next_duty_student_id]
        
        duty_text = f"👥 Дежурство на эту неделю:\n\n"
        duty_text += f"👤 Дежурный: {duty_student.get('first_name', 'Неизвестно')} @{duty_student.get('username', 'unknown')}\n"
        duty_text += f"📅 Неделя: {current_week}\n"
        duty_text += f"📆 Следующий: {next_duty_student.get('first_name', 'Неизвестно')} @{next_duty_student.get('username', 'unknown')}\n\n"
        
        duty_text += f"📋 Обязанности дежурного:\n"
        duty_text += f"• 🧹 Следить за чистотой класса\n"
        duty_text += f"• 📝 Стирать доску после уроков\n"
        duty_text += f"• 👨‍🏫 Помогать учителям\n"
        duty_text += f"• 🪟 Закрывать окна и выключать свет\n"
        duty_text += f"• 🚪 Закрывать класс после уроков\n"
        duty_text += f"• 🗑️ Выносить мусор\n\n"
        
        # Проверяем, дежурит ли текущий пользователь
        if str(message.from_user.id) == duty_student_id:
            duty_text += "⭐ Ты дежуришь на этой неделе! Спасибо за помощь! 💪"
        
        duty_text += f"\n\n🎲 Случайный факт: {get_random_fact()}"
    else:
        duty_text = "👥 Дежурные не назначены"
    
    bot.send_message(message.chat.id, duty_text, reply_markup=back_keyboard())

@bot.message_handler(func=lambda message: message.text == "📊 Мои оценки")
def my_grades_handler(message):
    """Мои оценки"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "my_grades")
    
    bot.send_message(
        message.chat.id,
        "📊 Твои оценки\n\nВыбери действие:",
        reply_markup=grades_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📊 Мои оценки" or message.text == "📋 По предметам")
def show_my_grades(message):
    """Показать оценки пользователя"""
    if not is_authorized(message.from_user.id):
        return
    
    user_id = message.from_user.id
    user_grades = grades.get(str(user_id), {})
    
    if not user_grades:
        bot.send_message(
            message.chat.id,
            "📊 У тебя пока нет оценок в системе!\n\n📚 Учись хорошо и они появятся! 💪",
            reply_markup=grades_menu()
        )
        return
    
    grades_text = f"📊 Твои оценки - {get_first_name_by_id(user_id)}:\n\n"
    
    total_grades = 0
    total_sum = 0
    
    for subject, subject_grades in user_grades.items():
        if subject_grades:
            avg_grade = sum(subject_grades) / len(subject_grades)
            grades_text += f"📚 {subject}:\n"
            grades_text += f"   Оценки: {', '.join(map(str, subject_grades))}\n"
            grades_text += f"   Средняя: {avg_grade:.2f}\n\n"
            
            total_grades += len(subject_grades)
            total_sum += sum(subject_grades)
    
    if total_grades > 0:
        overall_avg = total_sum / total_grades
        grades_text += f"🏆 Общий средний балл: {overall_avg:.2f}\n"
        grades_text += f"📈 Всего оценок: {total_grades}\n\n"
        
        if overall_avg >= 10:
            grades_text += "🌟 Отличные результаты! Так держать!"
        elif overall_avg >= 8:
            grades_text += "👍 Хорошие результаты! Можно еще лучше!"
        elif overall_avg >= 6:
            grades_text += "📈 Есть к чему стремиться! Не сдавайся!"
        else:
            grades_text += "💪 Нужно подтянуть учебу! Ты можешь лучше!"
    
    bot.send_message(message.chat.id, grades_text, reply_markup=grades_menu())

@bot.message_handler(func=lambda message: message.text == "📈 График оценок")
def grades_chart_handler(message):
    """График оценок"""
    if not is_authorized(message.from_user.id):
        return
    
    user_id = message.from_user.id
    chart_path = create_grades_chart(user_id)
    
    if chart_path and os.path.exists(chart_path):
        try:
            with open(chart_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id, 
                    photo,
                    caption=f"📈 График твоих оценок - {get_first_name_by_id(user_id)}",
                    reply_markup=grades_menu()
                )
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"❌ Ошибка отправки графика: {e}",
                reply_markup=grades_menu()
            )
    else:
        bot.send_message(
            message.chat.id,
            "📊 У тебя пока нет оценок для создания графика!\n\n📚 Учись хорошо и график появится!",
            reply_markup=grades_menu()
        )

@bot.message_handler(func=lambda message: message.text == "📈 Статистика")
def statistics_handler(message):
    """Обработчик статистики"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "statistics")
    
    today = datetime.date.today().isoformat()
    user_data = users.get(str(message.from_user.id), {})
    
    stats_text = f"📊 Статистика бота 8-А класса:\n\n"
    
    # Общая статистика
    stats_text += f"👥 Пользователей: {len(users)}\n"
    stats_text += f"📚 Домашних заданий: {len(homework)}\n"
    stats_text += f"📢 Объявлений: {len(important_messages)}\n"
    stats_text += f"🔥 Активных сегодня: {len(stats.get('daily_active', {}).get(today, []))}\n"
    stats_text += f"🎯 Тестов создано: {len(tests)}\n"
    stats_text += f"📝 Заметок создано: {len(notes)}\n\n"
    
    # Личная статистика
    stats_text += f"📱 Твоя статистика:\n"
    stats_text += f"📅 Зарегистрирован: {user_data.get('registered', 'Неизвестно')[:10]}\n"
    stats_text += f"📈 Команд использовано: {user_data.get('total_commands', 0)}\n"
    
    # Топ команд
    top_commands = sorted(stats.get('commands', {}).items(), key=lambda x: x[1], reverse=True)[:5]
    if top_commands:
        stats_text += f"\n🏆 Популярные команды:\n"
        for cmd, count in top_commands:
            stats_text += f"• {cmd}: {count} раз\n"
    
    stats_text += f"\n🌟 {get_motivational_quote()}"
    
    bot.send_message(message.chat.id, stats_text, reply_markup=back_keyboard())

@bot.message_handler(func=lambda message: message.text == "🎲 Развлечения")
def entertainment_handler(message):
    """Обработчик развлечений"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "entertainment")
    
    bot.send_message(
        message.chat.id,
        "🎲 Развлечения и интересности\n\nВыбери что хочешь:",
        reply_markup=entertainment_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🎲 Случайное число")
def random_number_handler(message):
    """Случайное число"""
    if not is_authorized(message.from_user.id):
        return
    
    number = random.randint(1, 100)
    bot.send_message(
        message.chat.id,
        f"🎲 Твое случайное число: {number}\n\n🔮 Может быть, это твоя счастливая цифра на сегодня!",
        reply_markup=entertainment_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🎭 Анекдот")
def joke_handler(message):
    """Анекдот"""
    if not is_authorized(message.from_user.id):
        return
    
    jokes = [
        "😄 Учитель: - Петя, назови мне пять диких животных!\nПетя: - Четыре волка и один тигр!",
        "😂 - Вовочка, что такое дистанционное обучение?\n- Это когда мама учится вместе со мной!",
        "🤣 Учитель математики - самый богатый человек: у него всегда есть корень из любой суммы!",
        "😆 - Почему программисты любят природу?\n- Потому что в ней нет багов!",
        "😁 Математик заходит в бар и заказывает пиво. Бармен спрашивает: 'Сколько?' Математик отвечает: 'Е в степени пи умножить на логарифм от бесконечности!'",
    ]
    
    joke = random.choice(jokes)
    bot.send_message(message.chat.id, joke, reply_markup=entertainment_menu())

@bot.message_handler(func=lambda message: message.text == "🧠 Интересный факт")
def fact_handler(message):
    """Интересный факт"""
    if not is_authorized(message.from_user.id):
        return
    
    fact = get_random_fact()
    bot.send_message(message.chat.id, fact, reply_markup=entertainment_menu())

@bot.message_handler(func=lambda message: message.text == "💪 Мотивация")
def motivation_handler(message):
    """Мотивационная цитата"""
    if not is_authorized(message.from_user.id):
        return
    
    quote = get_motivational_quote()
    bot.send_message(message.chat.id, quote, reply_markup=entertainment_menu())

@bot.message_handler(func=lambda message: message.text == "🌤️ Погода")
def weather_handler(message):
    """Погода"""
    if not is_authorized(message.from_user.id):
        return
    
    weather = get_weather()
    weather_text = f"🌤️ Погода сейчас:\n{weather}\n\n🧥 Одевайся по погоде!"
    bot.send_message(message.chat.id, weather_text, reply_markup=entertainment_menu())

@bot.message_handler(func=lambda message: message.text == "🎯 Тесты и опросы")
def tests_polls_handler(message):
    """Тесты и опросы"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "tests")
    
    if not tests:
        bot.send_message(
            message.chat.id,
            "🎯 Тестов пока нет!\n\n📚 Админы могут создать интересные тесты для класса!",
            reply_markup=back_keyboard()
        )
        return
    
    tests_text = "🎯 Доступные тесты:\n\n"
    
    for test_id, test_data in tests.items():
        tests_text += f"📝 {test_data['title']}\n"
        tests_text += f"📖 {test_data['description']}\n"
        tests_text += f"❓ Вопросов: {len(test_data['questions'])}\n"
        tests_text += f"👤 Создал: {test_data.get('created_by', 'Неизвестно')}\n\n"
    
    bot.send_message(message.chat.id, tests_text, reply_markup=back_keyboard())

@bot.message_handler(func=lambda message: message.text == "📝 Заметки")
def notes_handler(message):
    """Личные заметки"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "notes")
    
    user_notes = notes.get(str(message.from_user.id), [])
    
    if not user_notes:
        bot.send_message(
            message.chat.id,
            "📝 У тебя пока нет заметок!\n\n💡 Напиши 'Создать заметку: текст' чтобы создать первую заметку!",
            reply_markup=back_keyboard()
        )
        return
    
    notes_text = "📝 Твои заметки:\n\n"
    
    for i, note in enumerate(user_notes, 1):
        notes_text += f"{i}. {note['text'][:50]}{'...' if len(note['text']) > 50 else ''}\n"
        notes_text += f"   📅 {note.get('date', 'Неизвестно')}\n\n"
    
    notes_text += f"📊 Всего заметок: {len(user_notes)}\n\n"
    notes_text += "💡 Для создания новой заметки напиши:\n'Создать заметку: текст заметки'"
    
    bot.send_message(message.chat.id, notes_text, reply_markup=back_keyboard())

# ==================== ОБРАБОТЧИКИ ПОДДЕРЖКИ ====================

@bot.message_handler(func=lambda message: message.text == "💬 Написать в поддержку")
def support_handler(message):
    """Обработчик поддержки"""
    if not is_authorized(message.from_user.id):
        return
    
    support_text = f"""
💬 Поддержка бота 8-А класса

👨‍💻 Владелец: @{get_username_by_id(OWNER_ID)} (Артём)
👨‍💼 Староста: @{get_username_by_id(ADMIN_ID)} (Настя)

🤖 По техническим вопросам пиши владельцу
📚 По учебным вопросам пиши старосте

🙏 СПАСИБО АРТЕМУ И НАСТЕ ЗА РАБОТУ С БОТОМ!

Выбери кому написать:
    """
    
    bot.send_message(
        message.chat.id,
        support_text.strip(),
        reply_markup=support_menu()
    )

@bot.message_handler(func=lambda message: message.text.startswith("👑 Написать владельцу"))
def contact_owner_handler(message):
    """Связь с владельцем"""
    if not is_authorized(message.from_user.id):
        return
    
    contact_text = f"""
👑 Связь с владельцем

Артём (@{get_username_by_id(OWNER_ID)}) - создатель и владелец бота

📞 Пиши ему напрямую: @{get_username_by_id(OWNER_ID)}

🤖 Технические вопросы:
• Баги и ошибки бота
• Предложения по улучшению
• Новые функции
• Проблемы с доступом

🙏 Спасибо Артёму за создание этого крутого бота!
    """
    
    bot.send_message(message.chat.id, contact_text, reply_markup=support_menu())

@bot.message_handler(func=lambda message: message.text.startswith("👨‍💼 Написать старосте"))
def contact_admin_handler(message):
    """Связь со старостой"""
    if not is_authorized(message.from_user.id):
        return
    
    contact_text = f"""
👨‍💼 Связь со старостой

Настя (@{get_username_by_id(ADMIN_ID)}) - староста класса и администратор

📞 Пиши ей напрямую: @{get_username_by_id(ADMIN_ID)}

📚 Учебные вопросы:
• Домашние задания
• Расписание уроков
• Объявления
• Дежурство
• Оценки

🙏 Спасибо Насте за помощь в управлении ботом!
    """
    
    bot.send_message(message.chat.id, contact_text, reply_markup=support_menu())

# ==================== АДМИНСКИЕ ОБРАБОТЧИКИ ====================

@bot.message_handler(func=lambda message: message.text == "👑 Управление ДЗ")
def homework_admin_handler(message):
    """Админское управление ДЗ"""
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав администратора! Только староста и владелец могут управлять ДЗ.")
        return
    
    admin_type = "владелец" if is_owner(message.from_user.id) else "староста"
    bot.send_message(
        message.chat.id,
        f"👑 Управление домашними заданиями\n\n✅ Добро пожаловать, {admin_type}!\n\nВыберите действие:",
        reply_markup=homework_admin_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📈 Управление оценками")
def grades_admin_handler(message):
    """Админское управление оценками"""
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав администратора!")
        return
    
    bot.send_message(
        message.chat.id,
        "📈 Управление оценками класса\n\nВыберите действие:",
        reply_markup=grades_admin_menu()
    )

def grades_admin_menu():
    """Админское меню оценок"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "➕ Добавить оценку", "📊 Оценки по ученикам",
        "📚 Оценки по предметам", "📈 Статистика оценок",
        "❌ Удалить оценку", "📋 Экспорт оценок"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

@bot.message_handler(func=lambda message: message.text == "➕ Добавить оценку")
def add_grade_handler(message):
    """Добавление оценки"""
    if not is_admin(message.from_user.id):
        return
    
    students_list = "\n".join([f"• {users[uid].get('first_name', 'Неизвестно')} (ID: {uid})" 
                              for uid in users.keys() if users[uid].get('role') == 'student'])
    
    msg = bot.send_message(
        message.chat.id,
        f"📈 Добавление оценки\n\nУченики:\n{students_list}\n\nФормат: ID_ученика Предмет Оценка\nПример: 123456789 Математика 10",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_add_grade)

def process_add_grade(message):
    """Обработка добавления оценки"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, "❌ Неправильный формат! Используй: ID_ученика Предмет Оценка")
            return
        
        student_id = parts[0]
        subject = parts[1]
        grade = int(parts[2])
        
        if grade < 1 or grade > 12:
            bot.send_message(message.chat.id, "❌ Оценка должна быть от 1 до 12!")
            return
        
        if student_id not in users:
            bot.send_message(message.chat.id, "❌ Ученик не найден!")
            return
        
        # Добавляем оценку
        if student_id not in grades:
            grades[student_id] = {}
        
        if subject not in grades[student_id]:
            grades[student_id][subject] = []
        
        grades[student_id][subject].append(grade)
        save_data(GRADES_FILE, grades)
        
        student_name = users[student_id].get('first_name', 'Неизвестно')
        bot.send_message(
            message.chat.id,
            f"✅ Оценка добавлена!\n\n👤 Ученик: {student_name}\n📚 Предмет: {subject}\n📊 Оценка: {grade}\n👤 Добавил: {get_username_by_id(message.from_user.id)}",
            reply_markup=admin_menu()
        )
        
        # Уведомляем ученика
        try:
            bot.send_message(
                int(student_id),
                f"📊 Новая оценка!\n\n📚 Предмет: {subject}\n📈 Оценка: {grade}\n👤 Выставил: {get_username_by_id(message.from_user.id)}"
            )
        except:
            pass
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Оценка должна быть числом от 1 до 12!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == "📊 Оценки по ученикам")
def students_grades_handler(message):
    """Оценки всех учеников"""
    if not is_admin(message.from_user.id):
        return
    
    if not grades:
        bot.send_message(message.chat.id, "📊 Оценок пока нет в системе!")
        return
    
    grades_text = "📊 Оценки всех учеников:\n\n"
    
    for student_id, student_grades in grades.items():
        student_name = users.get(student_id, {}).get('first_name', 'Неизвестно')
        grades_text += f"👤 {student_name} (ID: {student_id}):\n"
        
        total_grades = 0
        total_sum = 0
        
        for subject, subject_grades in student_grades.items():
            if subject_grades:
                avg = sum(subject_grades) / len(subject_grades)
                grades_text += f"  📚 {subject}: {', '.join(map(str, subject_grades))} (ср: {avg:.1f})\n"
                total_grades += len(subject_grades)
                total_sum += sum(subject_grades)
        
        if total_grades > 0:
            overall_avg = total_sum / total_grades
            grades_text += f"  🏆 Общий средний: {overall_avg:.2f}\n\n"
        else:
            grades_text += "  📝 Нет оценок\n\n"
    
    bot.send_message(message.chat.id, grades_text, reply_markup=admin_menu())

@bot.message_handler(func=lambda message: message.text == "👥 Управление дежурством")
def duty_admin_handler(message):
    """Админское управление дежурством"""
    if not is_admin(message.from_user.id):
        return
    
    bot.send_message(
        message.chat.id,
        "👥 Управление дежурством\n\nВыберите действие:",
        reply_markup=duty_admin_menu()
    )

def duty_admin_menu():
    """Админское меню дежурства"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "📅 Текущее дежурство", "🔄 Сменить дежурного",
        "📋 График дежурства", "⚙️ Настроить дежурство"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

@bot.message_handler(func=lambda message: message.text == "🔄 Сменить дежурного")
def change_duty_handler(message):
    """Смена дежурного"""
    if not is_admin(message.from_user.id):
        return
    
    # Обновляем неделю дежурства
    duty_schedule["current_week"] = duty_schedule.get("current_week", 1) + 1
    save_data(DUTY_FILE, duty_schedule)
    
    # Определяем нового дежурного
    student_list = [uid for uid in users.keys() if users[uid].get('role') == 'student']
    
    if student_list:
        current_week = duty_schedule["current_week"]
        duty_index = (current_week - 1) % len(student_list)
        duty_student_id = student_list[duty_index]
        duty_student = users[duty_student_id]
        
        bot.send_message(
            message.chat.id,
            f"✅ Дежурный сменен!\n\n👤 Новый дежурный: {duty_student.get('first_name', 'Неизвестно')} @{duty_student.get('username', 'unknown')}\n📅 Неделя: {current_week}",
            reply_markup=admin_menu()
        )
        
        # Уведомляем всех о смене дежурного
        notification = f"🔄 Смена дежурного!\n\n👤 Новый дежурный: {duty_student.get('first_name', 'Неизвестно')} @{duty_student.get('username', 'unknown')}\n📅 Неделя: {current_week}"
        
        for user_id in users.keys():
            try:
                if users[user_id].get('notifications_enabled', True):
                    bot.send_message(int(user_id), notification)
                    time.sleep(0.05)
            except:
                pass
    else:
        bot.send_message(message.chat.id, "❌ Нет учеников для назначения дежурным!")

@bot.message_handler(func=lambda message: message.text == "📋 Посещаемость")
def attendance_admin_handler(message):
    """Управление посещаемостью"""
    if not is_admin(message.from_user.id):
        return
    
    bot.send_message(
        message.chat.id,
        "📋 Управление посещаемостью\n\nВыберите действие:",
        reply_markup=attendance_admin_menu()
    )

def attendance_admin_menu():
    """Админское меню посещаемости"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        "✅ Отметить присутствие", "❌ Отметить отсутствие",
        "📊 Статистика посещаемости", "📈 График посещаемости",
        "📅 Посещаемость по дням", "📋 Экспорт данных"
    ]
    markup.add(*[types.KeyboardButton(btn) for btn in buttons])
    markup.add(
        types.KeyboardButton("🔙 Главное меню"),
        types.KeyboardButton("💬 Написать в поддержку")
    )
    return markup

@bot.message_handler(func=lambda message: message.text == "✅ Отметить присутствие")
def mark_present_handler(message):
    """Отметить присутствие"""
    if not is_admin(message.from_user.id):
        return
    
    today = datetime.date.today().isoformat()
    students_list = "\n".join([f"• {users[uid].get('first_name', 'Неизвестно')} (ID: {uid})" 
                              for uid in users.keys() if users[uid].get('role') == 'student'])
    
    msg = bot.send_message(
        message.chat.id,
        f"✅ Отметка присутствия на {today}\n\nУченики:\n{students_list}\n\nНапишите ID ученика:",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, lambda m: process_attendance(m, 'present'))

@bot.message_handler(func=lambda message: message.text == "❌ Отметить отсутствие")
def mark_absent_handler(message):
    """Отметить отсутствие"""
    if not is_admin(message.from_user.id):
        return
    
    today = datetime.date.today().isoformat()
    students_list = "\n".join([f"• {users[uid].get('first_name', 'Неизвестно')} (ID: {uid})" 
                              for uid in users.keys() if users[uid].get('role') == 'student'])
    
    msg = bot.send_message(
        message.chat.id,
        f"❌ Отметка отсутствия на {today}\n\nУченики:\n{students_list}\n\nНапишите ID ученика:",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, lambda m: process_attendance(m, 'absent'))

def process_attendance(message, status):
    """Обработка отметки посещаемости"""
    if not is_admin(message.from_user.id):
        return
    
    student_id = message.text.strip()
    today = datetime.date.today().isoformat()
    
    if student_id not in users:
        bot.send_message(message.chat.id, "❌ Ученик не найден!")
        return
    
    if today not in attendance:
        attendance[today] = {}
    
    attendance[today][student_id] = status
    save_data(ATTENDANCE_FILE, attendance)
    
    student_name = users[student_id].get('first_name', 'Неизвестно')
    status_text = "присутствует" if status == 'present' else "отсутствует"
    status_emoji = "✅" if status == 'present' else "❌"
    
    bot.send_message(
        message.chat.id,
        f"{status_emoji} Отмечено!\n\n👤 {student_name} {status_text} {today}\n👤 Отметил: {get_username_by_id(message.from_user.id)}",
        reply_markup=admin_menu()
    )

@bot.message_handler(func=lambda message: message.text == "➕ Добавить ДЗ")
def add_homework_handler(message):
    """Добавление ДЗ"""
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав для добавления ДЗ! Обратись к старосте или владельцу.")
        return
    
    example_text = """
📝 Добавление домашнего задания

Формат: День_Предмет: Задание

Примеры:
• Понедельник_Математика: стр. 45, №123-127
• Вторник_Английский язык: выучить новые слова урок 8
• Среда_Физика: решить задачи из учебника стр. 89

Напиши свое ДЗ:"""
    
    msg = bot.send_message(
        message.chat.id,
        example_text,
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_add_homework)

def process_add_homework(message):
    """Обработка добавления ДЗ"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        text = message.text.strip()
        if ':' not in text:
            bot.send_message(
                message.chat.id, 
                "❌ Неправильный формат!\n\nИспользуй: День_Предмет: Текст\nПример: Понедельник_Математика: стр. 45"
            )
            return
        
        key, hw_text = text.split(':', 1)
        key = key.strip()
        hw_text = hw_text.strip()
        
        if '_' not in key:
            bot.send_message(message.chat.id, "❌ Неправильный формат! Используй подчеркивание между днем и предметом")
            return
        
        day, subject = key.split('_', 1)
        valid_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
        
        if day not in valid_days:
            bot.send_message(message.chat.id, f"❌ Неверный день! Используй: {', '.join(valid_days)}")
            return
        
        homework[key] = {
            'text': hw_text,
            'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            'added_by': get_username_by_id(message.from_user.id),
            'id': len(homework) + 1
        }
        
        save_data(HOMEWORK_FILE, homework)
        
        success_text = f"✅ ДЗ успешно добавлено!\n\n"
        success_text += f"📚 Предмет: {subject}\n"
        success_text += f"📅 День: {day}\n"
        success_text += f"📝 Задание: {hw_text}\n"
        success_text += f"👤 Добавил: {get_username_by_id(message.from_user.id)}\n"
        success_text += f"🆔 ID: {homework[key]['id']}"
        
        bot.send_message(
            message.chat.id,
            success_text,
            reply_markup=admin_menu()
        )
        
        # Уведомляем всех о новом ДЗ
        notification_text = f"🆕 Новое ДЗ!\n\n📚 {subject} ({day})\n📝 {hw_text}\n\n👤 Добавил: {get_username_by_id(message.from_user.id)}"
        for user_id in users.keys():
            try:
                if users[user_id].get('notifications_enabled', True):
                    bot.send_message(int(user_id), notification_text)
                    time.sleep(0.05)
            except:
                pass
        
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка при добавлении ДЗ: {e}",
            reply_markup=admin_menu()
        )

@bot.message_handler(func=lambda message: message.text == "📋 Список всех ДЗ")
def all_homework_admin_handler(message):
    """Список всех ДЗ для админа"""
    if not is_admin(message.from_user.id):
        return
    
    if not homework:
        bot.send_message(
            message.chat.id,
            "📝 Домашних заданий пока нет в системе!",
            reply_markup=admin_menu()
        )
        return
    
    hw_list = "📋 Все домашние задания в системе:\n\n"
    
    for i, (key, hw_data) in enumerate(homework.items(), 1):
        day, subject = key.split('_', 1) if '_' in key else (key, 'Неизвестный предмет')
        hw_list += f"{i}. 📚 {subject} ({day})\n"
        hw_list += f"   📝 {hw_data['text'][:60]}{'...' if len(hw_data['text']) > 60 else ''}\n"
        hw_list += f"   👤 {hw_data.get('added_by', 'Unknown')} | 📅 {hw_data.get('date', 'Unknown')}\n"
        hw_list += f"   🆔 ID: {hw_data.get('id', i)}\n\n"
    
    hw_list += f"📊 Всего заданий: {len(homework)}"
    
    bot.send_message(message.chat.id, hw_list, reply_markup=admin_menu())

@bot.message_handler(func=lambda message: message.text == "❌ Удалить ДЗ")
def delete_homework_handler(message):
    """Удаление ДЗ"""
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав для удаления ДЗ! Обратись к старосте или владельцу.")
        return
    
    if not homework:
        bot.send_message(message.chat.id, "📝 Нет ДЗ для удаления!")
        return
    
    hw_list = "❌ Удаление ДЗ\n\nНапиши точное название для удаления в формате День_Предмет:\n\n"
    for key in homework.keys():
        hw_list += f"• {key}\n"
    
    msg = bot.send_message(message.chat.id, hw_list, reply_markup=types.ForceReply())
    bot.register_next_step_handler(msg, process_delete_homework)

def process_delete_homework(message):
    """Обработка удаления ДЗ"""
    if not is_admin(message.from_user.id):
        return
    
    key = message.text.strip()
    
    if key in homework:
        deleted_hw = homework.pop(key)
        save_data(HOMEWORK_FILE, homework)
        
        bot.send_message(
            message.chat.id,
            f"✅ ДЗ удалено!\n\n📚 {key}\n📝 {deleted_hw['text']}\n👤 Удалил: {get_username_by_id(message.from_user.id)}",
            reply_markup=admin_menu()
        )
        
        # Уведомляем всех об удалении
        notification_text = f"❌ ДЗ удалено!\n\n📚 {key}\n👤 Удалил: {get_username_by_id(message.from_user.id)}"
        for user_id in users.keys():
            try:
                if users[user_id].get('notifications_enabled', True):
                    bot.send_message(int(user_id), notification_text)
                    time.sleep(0.05)
            except:
                pass
    else:
        bot.send_message(
            message.chat.id,
            f"❌ ДЗ '{key}' не найдено!",
            reply_markup=admin_menu()
        )

@bot.message_handler(func=lambda message: message.text == "📢 Отправить объявление")
def send_announcement_handler(message):
    """Отправка объявления"""
    if not is_admin(message.from_user.id):
        return
    
    msg = bot.send_message(
        message.chat.id,
        "📢 Напишите текст объявления:\n\n💡 Можно использовать emoji и форматирование!",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_send_announcement)

def process_send_announcement(message):
    """Обработка отправки объявления"""
    if not is_admin(message.from_user.id):
        return
    
    announcement_text = message.text.strip()
    
    # Сохраняем объявление
    announcement = {
        'text': announcement_text,
        'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        'author': get_username_by_id(message.from_user.id),
        'id': len(important_messages) + 1
    }
    
    important_messages.append(announcement)
    save_data(MESSAGES_FILE, important_messages)
    
    # Отправляем всем пользователям
    notification = f"📢 ВАЖНОЕ ОБЪЯВЛЕНИЕ!\n\n{announcement_text}\n\n👤 От: {announcement['author']}\n📅 {announcement['date']}"
    
    sent_count = 0
    for user_id in users.keys():
        try:
            if users[user_id].get('notifications_enabled', True):
                bot.send_message(int(user_id), notification)
                sent_count += 1
                time.sleep(0.05)
        except:
            pass
    
    bot.send_message(
        message.chat.id,
        f"✅ Объявление отправлено!\n\n📤 Отправлено {sent_count} пользователям\n📝 {announcement_text[:100]}{'...' if len(announcement_text) > 100 else ''}\n🆔 ID: {announcement['id']}",
        reply_markup=admin_menu()
    )

@bot.message_handler(func=lambda message: message.text == "👤 Список учеников")
def students_list_handler(message):
    """Список всех учеников"""
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ У тебя нет прав администратора!")
        return
    
    students_text = "👥 Список всех учеников класса:\n\n"
    
    student_count = 0
    admin_count = 0
    
    for user_id, user_data in users.items():
        role = user_data.get('role', 'student')
        if role == 'owner':
            role_icon = "👑"
            admin_count += 1
        elif role == 'admin':
            role_icon = "👨‍💼"
            admin_count += 1
        else:
            role_icon = "👤"
            student_count += 1
        
        first_name = user_data.get('first_name', '')
        username = user_data.get('username', 'Unknown')
        last_activity = user_data.get('last_activity', 'Неизвестно')[:10]
        total_commands = user_data.get('total_commands', 0)
        
        students_text += f"{role_icon} {first_name} @{username}\n"
        students_text += f"   🆔 ID: {user_id} | 👥 Группа: {user_data.get('group', 1)}\n"
        students_text += f"   📅 Регистрация: {user_data.get('registered', 'Неизвестно')[:10]}\n"
        students_text += f"   📱 Последняя активность: {last_activity}\n"
        students_text += f"   📊 Команд: {total_commands}\n\n"
    
    students_text += f"📊 Статистика:\n"
    students_text += f"• Всего: {len(users)}\n"
    students_text += f"• Админов: {admin_count}\n" 
    students_text += f"• Учеников: {student_count}\n"
    students_text += f"• В списке класса: {len(GROUP_1_IDS)}\n\n"
    students_text += f"🎓 Киевская инженерная гимназия 8-А класс"
    
    bot.send_message(
        message.chat.id,
        students_text,
        reply_markup=admin_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📊 Статистика админа")
def admin_statistics_handler(message):
    """Расширенная статистика для админа"""
    if not is_admin(message.from_user.id):
        return
    
    today = datetime.date.today().isoformat()
    
    # Активность за неделю
    week_activity = []
    for i in range(7):
        date = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
        active_count = len(stats.get('daily_active', {}).get(date, []))
        week_activity.append(active_count)
    
    stats_text = "📊 Подробная статистика бота:\n\n"
    
    # Пользователи
    stats_text += f"👥 Пользователи:\n"
    stats_text += f"• Зарегистрировано: {len(users)}\n"
    stats_text += f"• Активных сегодня: {len(stats.get('daily_active', {}).get(today, []))}\n"
    stats_text += f"• Средняя активность за неделю: {sum(week_activity)/7:.1f}\n\n"
    
    # Контент
    stats_text += f"📚 Контент:\n"
    stats_text += f"• Домашних заданий: {len(homework)}\n"
    stats_text += f"• Объявлений: {len(important_messages)}\n"
    stats_text += f"• Тестов: {len(tests)}\n"
    stats_text += f"• Событий: {len(events)}\n"
    stats_text += f"• Заметок: {sum(len(user_notes) for user_notes in notes.values())}\n\n"
    
    # Оценки
    total_grades = sum(len(subject_grades) for user_grades in grades.values() for subject_grades in user_grades.values())
    stats_text += f"📈 Оценки:\n"
    stats_text += f"• Всего оценок: {total_grades}\n"
    if total_grades > 0:
        avg_grade = sum(sum(subject_grades) for user_grades in grades.values() for subject_grades in user_grades.values()) / total_grades
        stats_text += f"• Средний балл класса: {avg_grade:.2f}\n"
    stats_text += "\n"
    
    # Топ команд
    top_commands = sorted(stats.get('commands', {}).items(), key=lambda x: x[1], reverse=True)[:5]
    if top_commands:
        stats_text += "🏆 Популярные команды:\n"
        for cmd, count in top_commands:
            stats_text += f"• {cmd}: {count}\n"
    
    stats_text += f"\n🤖 Бот работает стабильно!\n"
    stats_text += f"🙏 Спасибо Артёму и Насте за создание!"
    
    bot.send_message(message.chat.id, stats_text, reply_markup=admin_menu())

# ==================== ОБРАБОТЧИКИ УРОКОВ ====================

@bot.message_handler(func=lambda message: message.text.startswith("📚"))
def lesson_handler(message):
    """Обработчик клика по уроку"""
    if not is_authorized(message.from_user.id):
        return
    
    try:
        # Парсим день и предмет из кнопки: "📚 Понедельник|Математика"
        lesson_data = message.text.replace("📚 ", "")
        day, subject = lesson_data.split("|")
        
        user_id = message.from_user.id
        user_group = get_user_group(user_id)
        
        # Находим информацию об уроке
        group_key = f"group{user_group}"
        lessons = SCHEDULE.get(day, {}).get(group_key, [])
        
        lesson_info = None
        for lesson in lessons:
            if lesson['subject'] == subject:
                lesson_info = lesson
                break
        
        if not lesson_info:
            bot.send_message(message.chat.id, "❌ Урок не найден!")
            return
        
        # Проверяем ДЗ для урока
        hw_key = f"{day}_{subject}"
        
        lesson_text = f"📚 {subject} ({day})\n\n"
        lesson_text += f"🏫 Кабинет: {lesson_info['room']}\n"
        lesson_text += f"👨‍🏫 Учитель: {lesson_info['teacher']}\n"
        
        if lesson_info.get('group_note'):
            lesson_text += f"👥 {lesson_info['group_note']}\n"
        
        lesson_text += "\n"
        
        # Создаем кнопки в зависимости от статуса ДЗ
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        if hw_key in homework:
            # ДЗ есть - показываем его и кнопки для редактирования
            hw_data = homework[hw_key]
            lesson_text += f"📝 Домашнее задание:\n{hw_data['text']}\n\n"
            lesson_text += f"📅 Добавлено: {hw_data.get('date', 'Неизвестно')}\n"
            lesson_text += f"👤 Добавил: {hw_data.get('added_by', 'Неизвестно')}"
            
            if is_admin(user_id):
                markup.add(
                    types.KeyboardButton(f"✏️ Изменить ДЗ|{hw_key}"),
                    types.KeyboardButton(f"❌ Удалить ДЗ|{hw_key}")
                )
        else:
            # ДЗ нет - показываем варианты
            lesson_text += "📝 Домашнее задание:\n"
            
            if is_admin(user_id):
                # Для админов - кнопки управления
                markup.add(
                    types.KeyboardButton(f"➕ Добавить ДЗ|{hw_key}"),
                    types.KeyboardButton(f"❓ ДЗ еще не знаем|{hw_key}")
                )
                markup.add(
                    types.KeyboardButton(f"🚫 ДЗ нету|{hw_key}")
                )
                lesson_text += "Выберите действие:"
            else:
                # Для учеников - информация
                lesson_text += "❓ Пока не известно"
        
        # Кнопки навигации
        markup.add(
            types.KeyboardButton(f"📅 {day}"),
            types.KeyboardButton("🔙 Главное меню")
        )
        
        bot.send_message(message.chat.id, lesson_text, reply_markup=markup)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text.startswith("➕ Добавить ДЗ|"))
def add_lesson_homework_handler(message):
    """Добавление ДЗ к конкретному уроку"""
    if not is_admin(message.from_user.id):
        return
    
    hw_key = message.text.replace("➕ Добавить ДЗ|", "")
    day, subject = hw_key.split("_")
    
    msg = bot.send_message(
        message.chat.id,
        f"📝 Добавление ДЗ для урока:\n📚 {subject} ({day})\n\nНапишите текст домашнего задания:",
        reply_markup=types.ForceReply()
    )
    bot.register_next_step_handler(msg, lambda m: process_lesson_homework(m, hw_key, day, subject))

def process_lesson_homework(message, hw_key, day, subject):
    """Обработка добавления ДЗ к уроку"""
    if not is_admin(message.from_user.id):
        return
    
    hw_text = message.text.strip()
    
    homework[hw_key] = {
        'text': hw_text,
        'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        'added_by': get_username_by_id(message.from_user.id),
        'day': day,
        'subject': subject,
        'id': len(homework) + 1
    }
    
    save_data(HOMEWORK_FILE, homework)
    
    success_text = f"✅ ДЗ добавлено!\n\n"
    success_text += f"📚 {subject} ({day})\n"
    success_text += f"📝 {hw_text}\n"
    success_text += f"👤 Добавил: {get_username_by_id(message.from_user.id)}"
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(f"📚 {day}|{subject}"),
        types.KeyboardButton("🔙 Главное меню")
    )
    
    bot.send_message(message.chat.id, success_text, reply_markup=markup)
    
    # Уведомляем всех о новом ДЗ
    notification_text = f"🆕 Новое ДЗ!\n\n📚 {subject} ({day})\n📝 {hw_text}\n\n👤 Добавил: {get_username_by_id(message.from_user.id)}"
    for user_id in users.keys():
        try:
            if users[user_id].get('notifications_enabled', True) and str(user_id) != str(message.from_user.id):
                bot.send_message(int(user_id), notification_text)
                time.sleep(0.05)
        except:
            pass

@bot.message_handler(func=lambda message: message.text.startswith("❓ ДЗ еще не знаем|"))
def homework_unknown_handler(message):
    """ДЗ еще не известно"""
    if not is_admin(message.from_user.id):
        return
    
    hw_key = message.text.replace("❓ ДЗ еще не знаем|", "")
    day, subject = hw_key.split("_")
    
    homework[hw_key] = {
        'text': "❓ ДЗ еще не известно - ждем информации",
        'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        'added_by': get_username_by_id(message.from_user.id),
        'day': day,
        'subject': subject,
        'status': 'unknown'
    }
    
    save_data(HOMEWORK_FILE, homework)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(f"📚 {day}|{subject}"),
        types.KeyboardButton("🔙 Главное меню")
    )
    
    bot.send_message(
        message.chat.id,
        f"❓ Отмечено что ДЗ по {subject} ({day}) еще не известно",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text.startswith("🚫 ДЗ нету|"))
def homework_none_handler(message):
    """ДЗ нет"""
    if not is_admin(message.from_user.id):
        return
    
    hw_key = message.text.replace("🚫 ДЗ нету|", "")
    day, subject = hw_key.split("_")
    
    homework[hw_key] = {
        'text': "🚫 Домашнего задания нет",
        'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        'added_by': get_username_by_id(message.from_user.id),
        'day': day,
        'subject': subject,
        'status': 'none'
    }
    
    save_data(HOMEWORK_FILE, homework)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(f"📚 {day}|{subject}"),
        types.KeyboardButton("🔙 Главное меню")
    )
    
    bot.send_message(
        message.chat.id,
        f"🚫 Отмечено что ДЗ по {subject} ({day}) нет",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text.startswith("❌ Удалить ДЗ|"))
def delete_lesson_homework_handler(message):
    """Удаление ДЗ конкретного урока"""
    if not is_admin(message.from_user.id):
        return
    
    hw_key = message.text.replace("❌ Удалить ДЗ|", "")
    
    if hw_key in homework:
        deleted_hw = homework.pop(hw_key)
        save_data(HOMEWORK_FILE, homework)
        
        day, subject = hw_key.split("_")
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton(f"📚 {day}|{subject}"),
            types.KeyboardButton("🔙 Главное меню")
        )
        
        bot.send_message(
            message.chat.id,
            f"✅ ДЗ удалено!\n\n📚 {subject} ({day})\n👤 Удалил: {get_username_by_id(message.from_user.id)}",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "❌ ДЗ не найдено!")

# ==================== ОБРАБОТЧИКИ КНОПОК ====================

@bot.message_handler(func=lambda message: message.text == "🔙 Главное меню")
def back_to_main_menu(message):
    """Возврат в главное меню"""
    if not is_authorized(message.from_user.id):
        return
    
    # Обновляем активность пользователя
    if str(message.from_user.id) in users:
        users[str(message.from_user.id)]['last_activity'] = datetime.datetime.now().isoformat()
        users[str(message.from_user.id)]['total_commands'] = users[str(message.from_user.id)].get('total_commands', 0) + 1
        save_data(USERS_FILE, users)
    
    welcome_back_messages = [
        "🏠 Добро пожаловать в главное меню!",
        "🎓 Главное меню 8-А класса!",
        "🚀 Выбери что тебе нужно!",
        "📚 Главное меню бота!",
        "👋 С возвращением в меню!"
    ]
    
    bot.send_message(
        message.chat.id,
        random.choice(welcome_back_messages),
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "⚙️ Настройки")
def settings_handler(message):
    """Обработчик настроек"""
    if not is_authorized(message.from_user.id):
        return
    
    user_data = users.get(str(message.from_user.id), {})
    
    settings_text = f"⚙️ Настройки профиля:\n\n"
    settings_text += f"👤 Имя: {user_data.get('first_name', 'Неизвестно')}\n"
    settings_text += f"📱 Username: @{user_data.get('username', 'unknown')}\n"
    settings_text += f"👥 Группа: {user_data.get('group', 1)}\n"
    settings_text += f"📋 Роль: {user_data.get('role', 'student')}\n"
    settings_text += f"📅 Регистрация: {user_data.get('registered', 'Неизвестно')[:10]}\n"
    settings_text += f"📱 Последняя активность: {user_data.get('last_activity', 'Неизвестно')[:10]}\n"
    settings_text += f"📊 Команд использовано: {user_data.get('total_commands', 0)}\n\n"
    settings_text += f"🔔 Уведомления: {'✅ Включены' if user_data.get('notifications_enabled', True) else '❌ Выключены'}\n"
    settings_text += f"📚 Любимые предметы: {', '.join(user_data.get('favorite_subjects', [])) or '📝 Не выбраны'}\n\n"
    settings_text += f"💡 Для изменения настроек напиши админам!"
    
    bot.send_message(message.chat.id, settings_text, reply_markup=back_keyboard())

@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def help_handler(message):
    """Обработчик помощи"""
    if not is_authorized(message.from_user.id):
        return
    
    log_command(message.from_user.id, "help")
    show_help(message)

def show_help(message):
    """Показать помощь"""
    help_text = f"""
ℹ️ Справка по супер-боту 8-А класса

🤖 Этот бот поможет тебе во всем!

📅 Расписание:
• Смотреть уроки на любой день
• Узнавать время звонков
• Видеть текущий урок
• Получать расписание картинкой

📚 Домашние задания:
• Получать все ДЗ
• Смотреть задания на завтра/неделю
• Искать по предметам
• Следить за обновлениями

📊 Оценки:
• Просматривать свои оценки
• Строить графики успеваемости
• Сравнивать с классом
• Отслеживать прогресс

📢 Объявления:
• Читать важные сообщения
• Получать уведомления
• Архив объявлений

👥 Дежурство:
• Узнавать кто дежурный
• Смотреть обязанности
• График на неделю

🎯 Тесты и опросы:
• Участвовать в викторинах
• Проходить тесты знаний
• Голосовать в опросах

📝 Заметки:
• Создавать личные заметки
• Управлять списками дел
• Напоминания

🎲 Развлечения:
• Интересные факты
• Анекдоты и шутки
• Мотивационные цитаты
• Погода и случайности

📊 Статистика:
• Видеть активность класса
• Личная статистика
• Популярные команды

⚙️ Настройки:
• Управлять уведомлениями
• Настройки профиля
• Любимые предметы

💬 Поддержка:
• Связь с админами
• Техническая помощь
• Предложения

🚀 Специальные команды:
• /start - перезапуск бота
• /admin - админ панель (для админов)
• /help - эта справка
• /stats - быстрая статистика

📝 Создание заметок:
Напиши: "Создать заметку: текст"

🙏 СПАСИБО АРТЕМУ И НАСТЕ ЗА РАБОТУ С БОТОМ!

🏫 Киевская инженерная гимназия
👑 Владелец: @{get_username_by_id(OWNER_ID)}
👨‍💼 Староста: @{get_username_by_id(ADMIN_ID)}

💡 Этот бот постоянно развивается и становится лучше!
    """
    
    bot.send_message(message.chat.id, help_text.strip(), reply_markup=back_keyboard())

# ==================== ОБРАБОТЧИКИ СПЕЦИАЛЬНЫХ СООБЩЕНИЙ ====================

@bot.message_handler(func=lambda message: message.text.startswith("Создать заметку:"))
def create_note_handler(message):
    """Создание заметки"""
    if not is_authorized(message.from_user.id):
        return
    
    user_id = str(message.from_user.id)
    note_text = message.text.replace("Создать заметку:", "").strip()
    
    if not note_text:
        bot.send_message(
            message.chat.id,
            "❌ Пустая заметка!\n\n💡 Напиши: Создать заметку: текст заметки"
        )
        return
    
    if user_id not in notes:
        notes[user_id] = []
    
    new_note = {
        'text': note_text,
        'date': datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        'id': len(notes[user_id]) + 1
    }
    
    notes[user_id].append(new_note)
    save_data(NOTES_FILE, notes)
    
    bot.send_message(
        message.chat.id,
        f"✅ Заметка создана!\n\n📝 {note_text}\n📅 {new_note['date']}\n🆔 ID: {new_note['id']}\n\n📊 У тебя теперь {len(notes[user_id])} заметок"
    )

# ==================== СИСТЕМНЫЕ ФУНКЦИИ ====================

def daily_reminder():
    """Ежедневные напоминания"""
    while True:
        try:
            now = datetime.datetime.now()
            
            # Утреннее напоминание в 7:30
            if now.hour == 7 and now.minute == 30:
                today = get_current_day()
                if today in SCHEDULE:
                    reminder_text = f"🌅 Доброе утро, 8-А класс!\n\n"
                    reminder_text += f"📅 Сегодня {today}\n"
                    reminder_text += f"🌤️ Погода: {get_weather()}\n\n"
                    reminder_text += f"💪 {get_motivational_quote()}\n\n"
                    reminder_text += "📚 Не забудь проверить ДЗ в боте!"
                    
                    for user_id in users.keys():
                        try:
                            if users[user_id].get('notifications_enabled', True):
                                bot.send_message(int(user_id), reminder_text)
                                time.sleep(0.1)
                        except:
                            pass
                
                time.sleep(3600)  # Ждем час
            
            # Вечернее напоминание в 19:00
            elif now.hour == 19 and now.minute == 0:
                tomorrow = get_tomorrow_day()
                if tomorrow in SCHEDULE:
                    evening_text = f"🌆 Добрый вечер!\n\n"
                    evening_text += f"📅 Завтра {tomorrow}\n"
                    evening_text += f"📚 Не забудь подготовиться к урокам!\n"
                    evening_text += f"📝 Проверь ДЗ на завтра в боте\n\n"
                    evening_text += f"😴 Хорошего отдыха!"
                    
                    for user_id in users.keys():
                        try:
                            if users[user_id].get('notifications_enabled', True):
                                bot.send_message(int(user_id), evening_text)
                                time.sleep(0.1)
                        except:
                            pass
                
                time.sleep(3600)  # Ждем час
        except:
            pass
        
        time.sleep(60)  # Проверяем каждую минуту

def weekly_stats():
    """Еженедельная статистика"""
    while True:
        try:
            now = datetime.datetime.now()
            
            # Воскресенье в 18:00
            if now.weekday() == 6 and now.hour == 18 and now.minute == 0:
                stats_text = f"📊 Еженедельная статистика 8-А класса:\n\n"
                
                # Активность за неделю
                week_active = 0
                for i in range(7):
                    date = (datetime.date.today() - datetime.timedelta(days=i)).isoformat()
                    week_active += len(stats.get('daily_active', {}).get(date, []))
                
                stats_text += f"🔥 Активных за неделю: {week_active}\n"
                stats_text += f"📚 Новых ДЗ: {len([hw for hw in homework.values() if (datetime.datetime.now() - datetime.datetime.fromisoformat(hw.get('date', '2024-01-01 00:00')[:19])).days <= 7])}\n"
                stats_text += f"📢 Новых объявлений: {len([msg for msg in important_messages if (datetime.datetime.now() - datetime.datetime.fromisoformat(msg.get('date', '2024-01-01 00:00')[:19])).days <= 7])}\n\n"
                stats_text += f"🎯 Увидимся на следующей неделе!\n"
                stats_text += f"💪 {get_motivational_quote()}"
                
                for user_id in users.keys():
                    try:
                        if users[user_id].get('notifications_enabled', True):
                            bot.send_message(int(user_id), stats_text)
                            time.sleep(0.1)
                    except:
                        pass
                
                time.sleep(3600)
        except:
            pass
        
        time.sleep(3600)  # Проверяем каждый час

# Запуск напоминаний в отдельных потоках
reminder_thread = threading.Thread(target=daily_reminder, daemon=True)
reminder_thread.start()

stats_thread = threading.Thread(target=weekly_stats, daemon=True)
stats_thread.start()

# ==================== ОБРАБОТЧИК ВСЕХ ОСТАЛЬНЫХ СООБЩЕНИЙ ====================

@bot.message_handler(content_types=['text'])
def handle_all_messages(message):
    """Обработчик всех остальных текстовых сообщений"""
    if not is_authorized(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ У тебя нет доступа к боту!\n\n💬 Обратись в поддержку для получения доступа.",
            reply_markup=support_menu()
        )
        return
    
    # Обновляем активность
    user_id = str(message.from_user.id)
    if user_id in users:
        users[user_id]['last_activity'] = datetime.datetime.now().isoformat()
        users[user_id]['total_commands'] = users[user_id].get('total_commands', 0) + 1
        save_data(USERS_FILE, users)
    
    # Обрабатываем команды создания заметок
    if message.text.lower().startswith("создать заметку"):
        create_note_handler(message)
        return
    
    # Случайные ответы на неизвестные команды
    random_responses = [
        "🤔 Не понимаю эту команду. Попробуй воспользоваться меню!",
        "❓ Такой команды я не знаю. Нажми 'Помощь' для справки!",
        "🎯 Используй кнопки меню для навигации!",
        "💡 Нужна помощь? Нажми 'ℹ️ Помощь'!",
        "🚀 Выбери действие из главного меню!",
        "📚 Может быть, ты ищешь расписание или ДЗ?",
        f"🎲 Случайный факт: {get_random_fact()}",
        f"💪 {get_motivational_quote()}"
    ]
    
    response = random.choice(random_responses)
    
    # Добавляем подсказки для популярных запросов
    text = message.text.lower()
    if any(word in text for word in ['расписание', 'уроки', 'занятия']):
        response += "\n\n📅 Нажми 'Расписание' для просмотра уроков!"
    elif any(word in text for word in ['дз', 'домашние', 'задания', 'домашка']):
        response += "\n\n📚 Нажми 'Домашние задания' для просмотра ДЗ!"
    elif any(word in text for word in ['оценки', 'баллы', 'отметки']):
        response += "\n\n📊 Нажми 'Мои оценки' для просмотра успеваемости!"
    elif any(word in text for word in ['помощь', 'справка', 'help']):
        response += "\n\nℹ️ Нажми 'Помощь' для подробной справки!"
    
    bot.send_message(message.chat.id, response, reply_markup=main_menu())

# ==================== ЗАПУСК БОТА ====================

if __name__ == "__main__":
    print("🚀 Супер-бот 8-А класса запущен и работает на полную мощность!")
    print("🏫 Киевская инженерная гимназия")
    print("=" * 50)
    print("👑 Владелец:", OWNER_ID, f"(@{get_username_by_id(OWNER_ID)})")
    print("👨‍💼 Староста:", ADMIN_ID, f"(@{get_username_by_id(ADMIN_ID)})")
    print("👥 Учеников в списке:", len(GROUP_1_IDS))
    print("📚 Зарегистрированных пользователей:", len(users))
    print("📝 Домашних заданий:", len(homework))
    print("📢 Объявлений:", len(important_messages))
    print("📊 Оценок в системе:", sum(len(g) for g in grades.values() for g in g.values()) if grades else 0)
    print("🎯 Тестов создано:", len(tests))
    print("📝 Заметок создано:", sum(len(user_notes) for user_notes in notes.values()) if notes else 0)
    print("=" * 50)
    print("🌟 Функции бота:")
    print("• 📅 Расписание уроков с картинками")
    print("• 📚 Система домашних заданий")
    print("• 📊 Отслеживание оценок и статистики")
    print("• 📢 Система объявлений")
    print("• 👥 Управление дежурством")
    print("• 🎯 Тесты и опросы")
    print("• 📝 Личные заметки")
    print("• 🎲 Развлекательный контент")
    print("• 💬 Система поддержки")
    print("• 🔔 Напоминания и уведомления")
    print("• 📈 Графики и визуализация")
    print("• ⚙️ Гибкие настройки")
    print("=" * 50)
    print("🙏 СКАЖИТЕ СПАСИБО АРТЕМУ И НАСТЕ ЗА РАБОТУ С БОТОМ!")
    print("=" * 50)
    
    try:
        print("🔄 Запуск polling...")
        bot.polling(none_stop=True, interval=1, timeout=30)
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
        print("🔄 Перезапуск через 5 секунд...")
        time.sleep(5)
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e2:
            print(f"❌ Критическая ошибка: {e2}")
            print("🆘 Обратитесь к разработчику!")