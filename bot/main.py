import sys
import os

# Добавляем корневую папку в путь для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
import json
import random
from services.gigachat_generator import GigaChatGenerator
from config import config

class NKOBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        self.user_profiles = {}
        self.generator = GigaChatGenerator(config.GIGACHAT_API_KEY)
    
    def get_updates(self):
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"timeout": 100, "offset": self.last_update_id + 1}
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except:
            return {"result": []}
    
    def send_message(self, chat_id, text, reply_markup=None):
        try:
            url = f"{self.base_url}/sendMessage"
            params = {
                "chat_id": chat_id, 
                "text": text,
                "parse_mode": "HTML"
            }
            if reply_markup:
                params["reply_markup"] = json.dumps(reply_markup)
            requests.post(url, json=params, timeout=5)
        except Exception as e:
            print(f"Ошибка отправки: {e}")
    
    def create_keyboard(self, buttons):
        return {
            "keyboard": [[button] for button in buttons],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
    
    def create_inline_keyboard(self, buttons):
        return {
            "inline_keyboard": [[{"text": text, "callback_data": data}] for text, data in buttons]
        }
    
    def handle_start(self, chat_id, user_id):
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            self.send_message(
                chat_id, 
                f"👋 С возвращением!\n\nВаш профиль:\n🏢 {profile['name']}\n🎯 {profile['activity']}\n\nВыберите действие:",
                self.create_keyboard(["🎯 Создать пост", "📊 Мой профиль", "✏️ Изменить профиль"])
            )
        else:
            self.user_profiles[user_id] = {"step": "awaiting_name"}
            self.send_message(chat_id, "👋 Привет! Я помогу создавать контент для соцсетей вашей НКО!\n\nКак называется ваша организация?")
    
    def handle_profile_setup(self, chat_id, user_id, text):
        profile = self.user_profiles.get(user_id, {})
        
        if profile.get("step") == "awaiting_name":
            profile["name"] = text
            profile["step"] = "awaiting_activity"
            self.user_profiles[user_id] = profile
            self.send_message(chat_id, f"Отлично, {text}! 👏\n\nЧем занимается ваша организация?\nНапример: помощь животным, забота о пожилых, экология")
        
        elif profile.get("step") == "awaiting_activity":
            profile["activity"] = text
            profile["step"] = "completed"
            self.user_profiles[user_id] = profile
            self.send_message(
                chat_id, 
                f"🎉 Профиль сохранен!\n\n🏢 {profile['name']}\n🎯 {profile['activity']}\n\nТеперь можете создавать посты!",
                self.create_keyboard(["🎯 Создать пост", "📊 Мой профиль", "✏️ Изменить профиль"])
            )
    
    def handle_create_post(self, chat_id, user_id):
        profile = self.user_profiles.get(user_id)
        if not profile or profile.get("step") != "completed":
            self.send_message(chat_id, "❌ Сначала настройте профиль командой /start")
            return
        
        profile["step"] = "choosing_post_type"
        self.user_profiles[user_id] = profile
        
        keyboard = self.create_inline_keyboard([
            ("📊 Отчёт", "report"),
            ("📖 История", "story"),
            ("💰 Сбор средств", "fundraising"),
            ("🙏 Благодарность", "thanks"),
            ("💡 Факт", "fact")
        ])
        
        self.send_message(chat_id, "🎯 Выберите тип поста:", keyboard)
    
    def handle_post_type_selection(self, chat_id, user_id, post_type):
        profile = self.user_profiles.get(user_id)
        if profile:
            profile["step"] = "awaiting_topic"
            profile["current_post_type"] = post_type
            self.user_profiles[user_id] = profile
            
            post_types = {
                "report": "📊 отчёт о мероприятии",
                "story": "📖 историю подопечного",
                "fundraising": "💰 объявление о сборе средств", 
                "thanks": "🙏 благодарность волонтёрам",
                "fact": "💡 интересный факт"
            }
            
            self.send_message(
                chat_id, 
                f"Вы выбрали: {post_types.get(post_type, post_type)}\n\nТеперь опишите тему 1-2 предложениями:\nНапример: 'Вчера провели субботник в парке'"
            )
    
    def generate_content(self, chat_id, user_id, topic):
        profile = self.user_profiles.get(user_id)
        if not profile:
            return
        
        post_type = profile.get("current_post_type", "story")
        nko_name = profile.get("name", "Наша организация")
        nko_activity = profile.get("activity", "социальная помощь")
        
        self.send_message(chat_id, "🔄 Генерирую контент с помощью AI...")
        
        # Генерируем посты через GigaChat
        variants = self.generator.generate_post(nko_name, nko_activity, post_type, topic)
        
        # Отправляем варианты
        for i, variant in enumerate(variants, 1):
            self.send_message(chat_id, f"<b>Вариант {i}:</b>\n\n{variant}")
            if i < len(variants):
                self.send_message(chat_id, "➖➖➖➖➖➖➖➖➖➖")
        
        # Сбрасываем состояние
        profile["step"] = "completed"
        self.user_profiles[user_id] = profile
        
        # Предлагаем дальнейшие действия
        keyboard = self.create_inline_keyboard([
            ("🎯 Создать ещё пост", "create_more"),
            ("📊 Изменить профиль", "edit_profile")
        ])
        
        self.send_message(chat_id, "✅ Готово! Вы можете скопировать текст и использовать в соцсетях.\n\nЧто дальше?", keyboard)
    
    def handle_callback(self, chat_id, user_id, callback_data):
        try:
            if callback_data in ["report", "story", "fundraising", "thanks", "fact"]:
                self.handle_post_type_selection(chat_id, user_id, callback_data)
            elif callback_data == "create_more":
                self.handle_create_post(chat_id, user_id)
            elif callback_data == "edit_profile":
                # Безопасное удаление
                if user_id in self.user_profiles:
                    del self.user_profiles[user_id]
                self.handle_start(chat_id, user_id)
        except Exception as e:
            print(f"Ошибка в callback: {e}")
            self.send_message(chat_id, "❌ Произошла ошибка. Попробуйте снова.")
    
    def run(self):
        print("🚀 Бот НКО запущен...")
        print("📱 Найди @NTO_content_bot в Telegram")
        
        while True:
            try:
                updates = self.get_updates()
                
                if "result" in updates:
                    for update in updates["result"]:
                        self.last_update_id = update["update_id"]
                        
                        # Обработка callback-запросов
                        if "callback_query" in update:
                            try:
                                callback = update["callback_query"]
                                chat_id = callback["message"]["chat"]["id"]
                                user_id = callback["from"]["id"]
                                callback_data = callback["data"]
                                self.handle_callback(chat_id, user_id, callback_data)
                            except Exception as e:
                                print(f"Ошибка обработки callback: {e}")
                            continue
                        
                        if "message" in update:
                            message = update["message"]
                            chat_id = message["chat"]["id"]
                            user_id = message["from"]["id"]
                            text = message.get("text", "")
                            
                            # Обработка команд
                            if text == "/start":
                                self.handle_start(chat_id, user_id)
                            elif text == "🎯 Создать пост":
                                self.handle_create_post(chat_id, user_id)
                            elif text == "📊 Мой профиль":
                                profile = self.user_profiles.get(user_id, {})
                                if profile.get("step") == "completed":
                                    self.send_message(
                                        chat_id, 
                                        f"📊 Ваш профиль:\n\n🏢 {profile['name']}\n🎯 {profile['activity']}"
                                    )
                                else:
                                    self.send_message(chat_id, "❌ Профиль не настроен. Используйте /start")
                            elif text == "✏️ Изменить профиль":
                                # Безопасное удаление
                                if user_id in self.user_profiles:
                                    del self.user_profiles[user_id]
                                self.handle_start(chat_id, user_id)
                            else:
                                # Обработка текста в зависимости от состояния
                                profile = self.user_profiles.get(user_id, {})
                                if profile.get("step") in ["awaiting_name", "awaiting_activity"]:
                                    self.handle_profile_setup(chat_id, user_id, text)
                                elif profile.get("step") == "awaiting_topic":
                                    self.generate_content(chat_id, user_id, text)
                                else:
                                    self.send_message(chat_id, "Используйте кнопки меню для навигации 📱")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Ошибка в основном цикле: {e}")
                time.sleep(5)

if __name__ == "__main__":
    TOKEN = config.BOT_TOKEN
    bot = NKOBot(TOKEN)
    bot.run()