import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import random
import json
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8430638829:AAHKChULWFZyn2tfLuGSfDXmmJayf5KWJ2Q"
ADMIN_ID = 6185367393

DATA_FILE = "bot_data.json"

CHALLENGES = [
    "🏃 Зайдите в Brookhaven и заставьте 3 незнакомцев танцевать вместе с вами! Скиньте видео в подтверждение!",
    "⚡ Кто быстрее пройдет первый уровень в любом Obby-паркуре, используя только вид от первого лица?",
    "😂 Найдите в игре самый нелепый бесплатный скин и сделайте с ним селфи!",
    "🏆 Победите в любой игре на выживание без использования магазинных предметов!",
    "🎭 Устройте флешмоб в Tower of Hell - все должны упасть в одном месте одновременно!",
    "🏠 Постройте в Adopt Me самый странный дом и пригласите других игроков на экскурсию!",
    "⚔️ Победите босса в Dungeon Quest используя только стартовое оружие!",
    "🌊 Выживите 10 раундов в Natural Disaster Survival без использования VIP-серверов!",
    "🦈 В SharkBite проплывите от одного острова до другого без лодки (риск 100%)!",
    "💰 Заработайте 1000 монет в любом Tycoon-режиме за 15 минут!",
    "🎨 Создайте аватар только из бесплатных вещей, но чтобы он выглядел круче всех!",
    "🏃‍♂️ Пробегите марафон в Speed Run 4 не останавливаясь ни разу!",
    "👻 Напугайте 5 игроков в любом хоррор-режиме и запишите их реакцию!",
    "🎪 Устройте цирковое представление в MeepCity и соберите зрителей!",
    "🚗 Пройдите гонку в Jailbreak на самой медленной машине и всё равно выиграйте!"
]

ROBLOX_GAMES = [
    {"name": "Natural Disaster Survival", "link": "https://www.roblox.com/games/189707/Natural-Disaster-Survival"},
    {"name": "SharkBite", "link": "https://www.roblox.com/games/734159876/SharkBite"},
    {"name": "Tower of Hell", "link": "https://www.roblox.com/games/1962086868/Tower-of-Hell"},
    {"name": "Dungeon Quest", "link": "https://www.roblox.com/games/2414851778/Dungeon-Quest"},
    {"name": "Speed Run 4", "link": "https://www.roblox.com/games/183364845/Speed-Run-4"},
    {"name": "Zombie Attack", "link": "https://www.roblox.com/games/1240123653/Zombie-Attack"},
    {"name": "Super Bomb Survival", "link": "https://www.roblox.com/games/1537690962/Super-Bomb-Survival"},
    {"name": "Flood Escape 2", "link": "https://www.roblox.com/games/738339342/Flood-Escape-2"},
    {"name": "Murder Mystery 2", "link": "https://www.roblox.com/games/142823291/Murder-Mystery-2"},
    {"name": "Piggy", "link": "https://www.roblox.com/games/4623386862/Piggy"}
]

CIPHER_MAP = {
    'а': '🔥', 'б': '⚡', 'в': '💎', 'г': '🎮', 'д': '🏆',
    'е': '⭐', 'ё': '⭐', 'ж': '🌟', 'з': '💫', 'и': '✨',
    'й': '🎯', 'к': '🎪', 'л': '🎨', 'м': '🎭', 'н': '🎬',
    'о': '🎵', 'п': '🎸', 'р': '🎺', 'с': '🎻', 'т': '🥁',
    'у': '🎹', 'ф': '🎤', 'х': '🎧', 'ц': '📻', 'ч': '📱',
    'ш': '💻', 'щ': '⌨️', 'ъ': '🖥️', 'ы': '🖱️', 'ь': '💾',
    'э': '💿', 'ю': '📀', 'я': '🔊',
    ' ': '⬜', '.': '🔴', '!': '🔵', '?': '🟢', ',': '🟡'
}

DECIPHER_MAP = {v: k for k, v in CIPHER_MAP.items()}

def is_admin(user_id):
    return user_id == ADMIN_ID

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": {}, "challenges_completed": 0, "banned_users": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data["users"]:
        data["users"][user_id_str] = {
            "name": "",
            "coins": 0,
            "challenges_done": 0,
            "last_challenge": None
        }
        save_data(data)
    return data["users"][user_id_str]

def update_user_coins(user_id, coins_to_add):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str in data["users"]:
        data["users"][user_id_str]["coins"] += coins_to_add
        data["users"][user_id_str]["challenges_done"] += 1
    save_data(data)

def encrypt_message(text):
    text = text.lower()
    encrypted = ""
    for char in text:
        if char in CIPHER_MAP:
            encrypted += CIPHER_MAP[char]
        else:
            encrypted += char
    return encrypted

def decrypt_message(encrypted):
    decrypted = ""
    for emoji in encrypted:
        if emoji in DECIPHER_MAP:
            decrypted += DECIPHER_MAP[emoji]
        else:
            decrypted += emoji
    return decrypted

def create_leaderboard_image():
    data = load_data()
    users_list = []
    
    for user_id, user_info in data["users"].items():
        users_list.append((user_info["name"], user_info["coins"], user_info["challenges_done"]))
    
    users_list.sort(key=lambda x: x[1], reverse=True)
    
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 35)
        stats_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
    except:
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        stats_font = ImageFont.load_default()
    
    draw.text((400, 50), "🏆 ТУРНИРНАЯ ТАБЛИЦА 🏆", fill='#FFD700', anchor="mm", font=title_font)
    
    podium_colors = ['#FFD700', '#C0C0C0', '#CD7F32']
    podium_heights = [300, 250, 200]
    podium_y = [220, 270, 320]
    medals = ['🥇', '🥈', '🥉']
    
    for i in range(min(3, len(users_list))):
        x = 150 + (i * 250)
        y = podium_y[i]
        h = podium_heights[i]
        
        draw.rectangle([x, y, x + 200, y + h], fill=podium_colors[i], outline='white', width=3)
        
        draw.text((x + 100, y - 40), medals[i], fill='white', anchor="mm", font=title_font)
        
        name = users_list[i][0][:12]
        draw.text((x + 100, y + 30), name, fill='#1a1a2e', anchor="mm", font=name_font)
        
        coins_text = f"{users_list[i][1]} 💎"
        draw.text((x + 100, y + 80), coins_text, fill='#1a1a2e', anchor="mm", font=stats_font)
        
        challenges_text = f"{users_list[i][2]} заданий"
        draw.text((x + 100, y + 120), challenges_text, fill='#1a1a2e', anchor="mm", font=stats_font)
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_id_str = str(user.id)
    
    if user.id in data.get("banned_users", []):
        await update.message.reply_text("❌ Ты забанен в этом боте!")
        return
    
    if user_id_str not in data["users"]:
        data["users"][user_id_str] = {
            "name": user.first_name,
            "coins": 0,
            "challenges_done": 0,
            "last_challenge": None
        }
        save_data(data)
    
    keyboard = [
        [InlineKeyboardButton("🎯 Дать задание", callback_data='challenge')],
        [InlineKeyboardButton("🎮 Рандомная игра", callback_data='random_game')],
        [InlineKeyboardButton("🏆 Турнирная таблица", callback_data='leaderboard')],
        [InlineKeyboardButton("🔐 Зашифровать", callback_data='encrypt'),
         InlineKeyboardButton("🔓 Расшифровать", callback_data='decrypt')],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
    ]
    
    if is_admin(user.id):
        keyboard.append([InlineKeyboardButton("⚙️ АДМИН-ПАНЕЛЬ", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""🎮 *Привет, {user.first_name}!*

Добро пожаловать в *Roblox Boss Challenge*! 🏆

Я буду давать тебе и твоим друзьям крутые задания в Роблоксе!

За каждое выполненное задание ты получаешь *Роблокс-коины* 💎

Выбери действие ниже:"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if not is_admin(query.from_user.id):
        await query.answer("❌ У тебя нет доступа к админ-панели!", show_alert=True)
        return
    
    await query.answer()
    
    data = load_data()
    total_users = len(data["users"])
    total_challenges = sum(u["challenges_done"] for u in data["users"].values())
    total_coins = sum(u["coins"] for u in data["users"].values())
    
    keyboard = [
        [InlineKeyboardButton("👥 Список пользователей", callback_data='admin_users')],
        [InlineKeyboardButton("💎 Выдать коины", callback_data='admin_give_coins')],
        [InlineKeyboardButton("🔄 Сбросить статистику", callback_data='admin_reset_stats')],
        [InlineKeyboardButton("📊 Статистика бота", callback_data='admin_stats')],
        [InlineKeyboardButton("📢 Рассылка", callback_data='admin_broadcast')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    admin_text = f"""⚙️ *АДМИН-ПАНЕЛЬ*

📊 *Статистика:*
👥 Пользователей: {total_users}
✅ Выполнено заданий: {total_challenges}
💎 Всего коинов: {total_coins}

Выбери действие:"""
    
    await query.edit_message_text(admin_text, parse_mode='Markdown', reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = load_data()
    if query.from_user.id in data.get("banned_users", []):
        await query.answer("❌ Ты забанен!", show_alert=True)
        return
    
    if query.data == 'challenge':
        challenge = random.choice(CHALLENGES)
        user_data = get_user_data(query.from_user.id)
        
        data = load_data()
        data["users"][str(query.from_user.id)]["last_challenge"] = challenge
        save_data(data)
        
        keyboard = [
            [InlineKeyboardButton("✅ Выполнил! (+50 коинов)", callback_data='complete_challenge')],
            [InlineKeyboardButton("🔄 Другое задание", callback_data='challenge')],
            [InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎯 *НОВОЕ ЗАДАНИЕ:*\n\n{challenge}\n\n💰 Награда: 50 Роблокс-коинов",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'complete_challenge':
        await query.edit_message_text(
            "📸 *ПОДТВЕРЖДЕНИЕ ЗАДАНИЯ*\n\n⚠️ Для получения коинов нужно подтвердить выполнение!\n\n📷 Отправь скриншот из игры, где видно что ты выполнил задание!\n\n💡 Просто скинь любое фото из Роблокса",
            parse_mode='Markdown'
        )
        context.user_data['waiting_screenshot'] = True
    
    elif query.data == 'random_game':
        game = random.choice(ROBLOX_GAMES)
        
        keyboard = [
            [InlineKeyboardButton("🔄 Другая игра", callback_data='random_game')],
            [InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎮 *РАНДОМНАЯ ИГРА:*\n\n*{game['name']}*\n\n🔗 {game['link']}\n\nЗаходи и зови друзей! 🚀",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'leaderboard':
        data = load_data()
        users_list = []
        
        for user_id, user_info in data["users"].items():
            users_list.append((user_info["name"], user_info["coins"], user_info["challenges_done"]))
        
        users_list.sort(key=lambda x: x[1], reverse=True)
        
        leaderboard_text = "🏆 *ТУРНИРНАЯ ТАБЛИЦА*\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (name, coins, challenges) in enumerate(users_list[:10]):
            medal = medals[i] if i < 3 else f"{i+1}."
            leaderboard_text += f"{medal} *{name}* - {coins} 💎 ({challenges} заданий)\n"
        
        keyboard = [
            [InlineKeyboardButton("📸 Картинка таблицы", callback_data='leaderboard_image')],
            [InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(leaderboard_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'leaderboard_image':
        await query.message.reply_text("📸 Создаю крутую картинку... Секунду!")
        
        try:
            image_buffer = create_leaderboard_image()
            await query.message.reply_photo(
                photo=image_buffer,
                caption="🏆 Вот ваша турнирная таблица! Кто сегодня на топе? 🔥"
            )
        except Exception as e:
            await query.message.reply_text(f"❌ Ошибка при создании картинки: {str(e)}\n\nПопробуй команду /top для текстовой версии")
    
    elif query.data == 'encrypt':
        await query.edit_message_text(
            "🔐 *РЕЖИМ ШИФРОВАНИЯ*\n\nНапиши мне сообщение, и я зашифрую его в эмодзи-код!\n\nПример: 'привет' → 🎸🎺✨⭐🥁",
            parse_mode='Markdown'
        )
        context.user_data['mode'] = 'encrypt'
    
    elif query.data == 'decrypt':
        await query.edit_message_text(
            "🔓 *РЕЖИМ РАСШИФРОВКИ*\n\nОтправь мне зашифрованное сообщение (эмодзи), и я переведу его в текст!\n\nПример: 🎸🎺✨⭐🥁 → 'привет'",
            parse_mode='Markdown'
        )
        context.user_data['mode'] = 'decrypt'
    
    elif query.data == 'help':
        help_text = """ℹ️ *ПОЛНАЯ ИНСТРУКЦИЯ*

🎯 *Дать задание*
Получи случайный челлендж в Роблоксе. Выполни его и жми "Выполнил!" чтобы получить 50 коинов!

🎮 *Рандомная игра*
Не знаешь во что поиграть? Жми сюда и бот выберет крутую игру для вас!

🏆 *Турнирная таблица*
Посмотри кто сейчас на первом месте! Можно получить картинку с подиумом 🥇🥈🥉

🔐 *Зашифровать*
Преврати свой текст в секретный эмодзи-код! Отправь друзьям зашифровку.

🔓 *Расшифровать*
Получил от друга эмодзи? Расшифруй их здесь!

📱 *КОМАНДЫ:*
/start - Главное меню
/top - Турнирная таблица
/stats - Твоя статистика
/help - Эта инструкция

💡 *КАК ИГРАТЬ:*
1️⃣ Получи задание
2️⃣ Выполни его в Роблоксе
3️⃣ Жми "Выполнил!"
4️⃣ Получи 50 коинов
5️⃣ Стань лучшим!

🎮 Соревнуйся с друзьями и поднимайся в топ!"""
        keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'menu':
        keyboard = [
            [InlineKeyboardButton("🎯 Дать задание", callback_data='challenge')],
            [InlineKeyboardButton("🎮 Рандомная игра", callback_data='random_game')],
            [InlineKeyboardButton("🏆 Турнирная таблица", callback_data='leaderboard')],
            [InlineKeyboardButton("🔐 Зашифровать", callback_data='encrypt'),
             InlineKeyboardButton("🔓 Расшифровать", callback_data='decrypt')],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
        ]
        
        if is_admin(query.from_user.id):
            keyboard.append([InlineKeyboardButton("⚙️ АДМИН-ПАНЕЛЬ", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎮 *Roblox Boss Challenge*\n\nВыбери действие:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'admin_panel':
        await admin_panel(update, context)
    
    elif query.data == 'admin_users':
        if not is_admin(query.from_user.id):
            await query.answer("❌ Нет доступа!", show_alert=True)
            return
        
        data = load_data()
        users_text = "👥 *СПИСОК ПОЛЬЗОВАТЕЛЕЙ:*\n\n"
        
        for user_id, user_info in data["users"].items():
            users_text += f"👤 {user_info['name']} (ID: `{user_id}`)\n💎 {user_info['coins']} коинов | ✅ {user_info['challenges_done']} заданий\n\n"
        
        keyboard = [[InlineKeyboardButton("⚙️ Назад", callback_data='admin_panel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(users_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'admin_give_coins':
        if not is_admin(query.from_user.id):
            await query.answer("❌ Нет доступа!", show_alert=True)
            return
        
        await query.edit_message_text(
            "💎 *ВЫДАТЬ КОИНЫ*\n\nОтправь сообщение в формате:\n`ID количество`\n\nПример: `123456789 100`",
            parse_mode='Markdown'
        )
        context.user_data['admin_mode'] = 'give_coins'
    
    elif query.data == 'admin_reset_stats':
        if not is_admin(query.from_user.id):
            await query.answer("❌ Нет доступа!", show_alert=True)
            return
        
        keyboard = [
            [InlineKeyboardButton("✅ ДА, СБРОСИТЬ ВСЁ", callback_data='admin_reset_confirm')],
            [InlineKeyboardButton("❌ Отмена", callback_data='admin_panel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚠️ *ВНИМАНИЕ!*\n\nТы уверен что хочешь сбросить всю статистику всех игроков?\n\nЭто действие нельзя отменить!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'admin_reset_confirm':
        if not is_admin(query.from_user.id):
            await query.answer("❌ Нет доступа!", show_alert=True)
            return
        
        data = load_data()
        for user_id in data["users"]:
            data["users"][user_id]["coins"] = 0
            data["users"][user_id]["challenges_done"] = 0
        save_data(data)
        
        keyboard = [[InlineKeyboardButton("⚙️ Админ-панель", callback_data='admin_panel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "✅ *СТАТИСТИКА СБРОШЕНА!*\n\nВсе игроки начинают с нуля!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif query.data == 'admin_stats':
        if not is_admin(query.from_user.id):
            await query.answer("❌ Нет доступа!", show_alert=True)
            return
        
        data = load_data()
        total_users = len(data["users"])
        total_challenges = sum(u["challenges_done"] for u in data["users"].values())
        total_coins = sum(u["coins"] for u in data["users"].values())
        
        most_active = max(data["users"].items(), key=lambda x: x[1]["challenges_done"], default=(None, {"name": "Никто", "challenges_done": 0}))
        
        stats_text = f"""📊 *СТАТИСТИКА БОТА*

👥 Всего пользователей: {total_users}
✅ Выполнено заданий: {total_challenges}
💎 Всего коинов: {total_coins}
📈 Среднее заданий: {total_challenges // total_users if total_users > 0 else 0}

🏆 Самый активный: {most_active[1]["name"]} ({most_active[1]["challenges_done"]} заданий)"""
        
        keyboard = [[InlineKeyboardButton("⚙️ Админ-панель", callback_data='admin_panel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif query.data == 'admin_broadcast':
        if not is_admin(query.from_user.id):
            await query.answer("❌ Нет доступа!", show_alert=True)
            return
        
        await query.edit_message_text(
            "📢 *РАССЫЛКА*\n\nОтправь сообщение которое хочешь разослать всем пользователям бота:",
            parse_mode='Markdown'
        )
        context.user_data['admin_mode'] = 'broadcast'

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Перевіряємо, чи ми чекаємо скриншот
    if not context.user_data.get('waiting_screenshot'):
        return

    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id in data["users"]:
        # Нараховуємо 50 коїнів
        data["users"][user_id]["coins"] += 50
        data["users"][user_id]["challenges_done"] += 1
        data["users"][user_id]["last_challenge"] = None
        save_data(data)
        
        # Вимикаємо режим очікування
        context.user_data['waiting_screenshot'] = False

        keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "✅ *ЗАДАНИЕ ВЫПОЛНЕНО!*\n\n📸 Скриншот получен. Тебе начислено *50 Роблокс-коинов*! 💎\n\nПродолжай в том же духе!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("❌ Ошибка: сначала нажми /start")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    admin_mode = context.user_data.get('admin_mode')
    
    data = load_data()
    if update.effective_user.id in data.get("banned_users", []):
        await update.message.reply_text("❌ Ты забанен!")
        return
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if admin_mode and is_admin(update.effective_user.id):
        if admin_mode == 'give_coins':
            try:
                parts = update.message.text.split()
                user_id = parts[0]
                coins = int(parts[1])
                
                data = load_data()
                if user_id in data["users"]:
                    data["users"][user_id]["coins"] += coins
                    save_data(data)
                    await update.message.reply_text(
                        f"✅ Выдано {coins} коинов пользователю {data['users'][user_id]['name']}!",
                        reply_markup=reply_markup
                    )
                else:
                    await update.message.reply_text("❌ Пользователь не найден!", reply_markup=reply_markup)
            except:
                await update.message.reply_text("❌ Неверный формат! Используй: ID количество", reply_markup=reply_markup)
            
            context.user_data['admin_mode'] = None
        
        elif admin_mode == 'broadcast':
            data = load_data()
            text = update.message.text
            success = 0
            failed = 0
            
            for user_id in data["users"]:
                try:
                    await context.bot.send_message(chat_id=int(user_id), text=f"📢 *СООБЩЕНИЕ ОТ АДМИНА:*\n\n{text}", parse_mode='Markdown')
                    success += 1
                except:
                    failed += 1
            
                    # Це кінець блоку розсилки адміна
        await update.message.reply_text(
            f"✅ Рассылка завершена!\n\n✅ Успешно: {success}\n❌ Ошибок: {failed}",
            reply_markup=reply_markup
        )
        context.user_data['admin_mode'] = None
        return # Цей return виходить з функції, якщо спрацювала розсилка

    # --- ПЕРЕВІР ЦЕЙ ВІДСТУП НИЖЧЕ ---
    if mode == 'encrypt':
        encrypted = encrypt_message(update.message.text)
        
        # Відправляємо зашифрований текст
        await update.message.reply_text(
            f"🔐 *ЗАШИФРОВАНО:*\n\n`{encrypted}`\n\nОтправь это друзьям! Они смогут расшифровать через бота 😎",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

        
        # Отправляем зашифрованный текст отдельным сообщением для копирования
        await update.message.reply_text(
            encrypted,
            reply_to_message_id=update.message.message_id
        )
        
        context.user_data['mode'] = None

    
    elif mode == 'decrypt':
        decrypted = decrypt_message(update.message.text)
        await update.message.reply_text(
            f"🔓 *РАСШИФРОВАНО:*\n\n{decrypted}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        context.user_data['mode'] = None
    
    else:
        await update.message.reply_text(
            "Используй кнопки меню или команду /start 😊",
            reply_markup=reply_markup
        )


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    
    if update.effective_user.id in data.get("banned_users", []):
        await update.message.reply_text("❌ Ты забанен!")
        return
    
    users_list = []
    
    for user_id, user_info in data["users"].items():
        users_list.append((user_info["name"], user_info["coins"], user_info["challenges_done"]))
    
    users_list.sort(key=lambda x: x[1], reverse=True)
    
    leaderboard_text = "🏆 *ТОП ПРО-ГЕЙМЕРОВ*\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, (name, coins, challenges) in enumerate(users_list[:10]):
        medal = medals[i] if i < 3 else f"{i+1}."
        leaderboard_text += f"{medal} *{name}* - {coins} 💎 ({challenges} заданий)\n"
    
    keyboard = [
        [InlineKeyboardButton("📸 Картинка таблицы", callback_data='leaderboard_image')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(leaderboard_text, parse_mode='Markdown', reply_markup=reply_markup)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    
    if update.effective_user.id in data.get("banned_users", []):
        await update.message.reply_text("❌ Ты забанен!")
        return
    
    user_data = get_user_data(update.effective_user.id)
    
    stats_text = f"""📊 *ТВОЯ СТАТИСТИКА*

👤 Игрок: {update.effective_user.first_name}
💎 Коины: {user_data['coins']}
✅ Выполнено заданий: {user_data['challenges_done']}

🎮 Продолжай в том же духе!"""
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(stats_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    
    if update.effective_user.id in data.get("banned_users", []):
        await update.message.reply_text("❌ Ты забанен!")
        return
    
    help_text = """ℹ️ *ПОЛНАЯ ИНСТРУКЦИЯ*

🎯 *Дать задание*
Получи случайный челлендж в Роблоксе. Выполни его и жми "Выполнил!" чтобы получить 50 коинов!

🎮 *Рандомная игра*
Не знаешь во что поиграть? Жми сюда и бот выберет крутую игру для вас!

🏆 *Турнирная таблица*
Посмотри кто сейчас на первом месте! Можно получить картинку с подиумом 🥇🥈🥉

🔐 *Зашифровать*
Преврати свой текст в секретный эмодзи-код! Отправь друзьям зашифровку.

🔓 *Расшифровать*
Получил от друга эмодзи? Расшифруй их здесь!

📱 *КОМАНДЫ:*
/start - Главное меню
/top - Турнирная таблица
/stats - Твоя статистика
/help - Эта инструкция

💡 *КАК ИГРАТЬ:*
1️⃣ Получи задание
2️⃣ Выполни его в Роблоксе
3️⃣ Жми "Выполнил!"
4️⃣ Получи 50 коинов
5️⃣ Стань лучшим!

🎮 Соревнуйся с друзьями и поднимайся в топ!

🎁 *СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ:*
Используй бота активно с друзьями в течение 72 часов и получи 100 РОБАКСОВ! 💰🔥"""
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)

def main():
    # Створюємо додаток
    application = Application.builder().token(TOKEN).build()
    
    # Команди
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("top", top_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обробка кнопок
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # --- НОВИЙ ОБРОБНИК ФОТО ---
    # Важливо: він має бути вище за MessageHandler з текстом
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    
    # Обробка тексту (шифрування, розшифрування та адмін-розсилка)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Roblox Boss Challenge Bot запущен!")
    
    # Запуск бота (відступ має бути рівно 4 пробіли від краю def)
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
