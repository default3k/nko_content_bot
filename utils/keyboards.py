from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["🎯 Создать пост", "📊 Мой профиль"]
    ], resize_keyboard=True)

def get_post_types_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 Отчёт", callback_data="post_type_report"),
            InlineKeyboardButton("📖 История", callback_data="post_type_story"),
        ],
        [
            InlineKeyboardButton("💰 Сбор средств", callback_data="post_type_fundraising"),
            InlineKeyboardButton("🙏 Благодарность", callback_data="post_type_thanks"),
        ],
        [
            InlineKeyboardButton("💡 Факт", callback_data="post_type_fact")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)