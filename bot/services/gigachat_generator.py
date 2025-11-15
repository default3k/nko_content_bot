import requests
import json
import base64
import uuid
from typing import List

class GigaChatGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.access_token = None
        self.token_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    def _get_access_token(self) -> str:
        """Получаем access token используя API ключ"""
        if self.access_token:
            return self.access_token
            
        try:
            # Декодируем Base64 ключ
            decoded = base64.b64decode(self.api_key).decode('utf-8')
            client_id, client_secret = decoded.split(':', 1)
            
            # Создаем Basic Auth
            auth_string = f"{client_id}:{client_secret}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4())
            }
            
            data = {'scope': 'GIGACHAT_API_PERS'}
            
            response = requests.post(self.token_url, headers=headers, data=data, verify=False)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                return self.access_token
            else:
                raise Exception(f"Ошибка получения токена: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка GigaChat: {e}")
            raise
    
    def _clean_content(self, content: str) -> str:
        """Очищает контент от лишних символов и форматирования"""
        # Убираем лишние символы
        content = content.replace('###', '').replace('---', '').replace('::', '')
        
        # Убираем пустые строки и лишние переносы
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith(':') and line != '###' and line != '---':
                lines.append(line)
        
        return '\n'.join(lines)
    
    def generate_post(self, nko_name: str, nko_activity: str, post_type: str, topic: str) -> List[str]:
        """Генерирует посты через GigaChat"""
        
        # Проверяем на чувствительный контент
        sensitive_words = ["анальн", "дебошир", "ворова", "пердун", "присторел", "деняг"]
        text_to_check = f"{nko_name} {nko_activity} {topic}".lower()
        
        if any(word in text_to_check for word in sensitive_words):
            return ["⚠️ Извините, исходные данные содержат некорректные моменты. Отредактируйте тему или название организации."]
        
        try:
            access_token = self._get_access_token()
            
            prompt = f"""
Организация: {nko_name}
Деятельность: {nko_activity}
Тип поста: {post_type}
Тема: {topic}

Создай 2 РАЗНЫХ поста для социальных сетей. 

ВАЖНЫЕ ТРЕБОВАНИЯ:
- Длина до 250 символов каждый
- Обязательно упомяни название организации "{nko_name}"
- Упомяни деятельность: {nko_activity}
- Естественный, эмоциональный язык
- Конкретный призыв к действию
- 3-5 релевантных хештегов
- Без лишних символов (---, ###, ::)

ПЕРВЫЙ ВАРИАНТ:

[здесь первый пост]

ВТОРОЙ ВАРИАНТ:

[здесь второй пост]
"""
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, verify=False, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Проверяем на блокировку
                if "генеративные языковые модели" in content.lower():
                    return ["⚠️ Извините, исходные данные содержат некорректные моменты. Отредактируйте тему или название организации."]
                
                # Разделяем на варианты и очищаем
                variants = []
                
                if "ПЕРВЫЙ ВАРИАНТ" in content and "ВТОРОЙ ВАРИАНТ" in content:
                    # Разделяем по меткам вариантов
                    parts = content.split("ВТОРОЙ ВАРИАНТ")
                    if len(parts) >= 2:
                        variant1 = parts[0].replace("ПЕРВЫЙ ВАРИАНТ", "").strip()
                        variant2 = parts[1].strip()
                        
                        # Очищаем оба варианта
                        variant1 = self._clean_content(variant1)
                        variant2 = self._clean_content(variant2)
                        
                        variants = [variant1, variant2]
                
                if not variants or len(variants[0]) < 50:
                    # Если не удалось разделить или посты слишком короткие, используем резервные
                    return self._get_quality_fallback_post(nko_name, nko_activity, post_type, topic)
                
                return variants[:2]
            else:
                return self._get_quality_fallback_post(nko_name, nko_activity, post_type, topic)
            
        except Exception as e:
            print(f"❌ Ошибка GigaChat: {e}")
            return self._get_quality_fallback_post(nko_name, nko_activity, post_type, topic)
    
    def _get_quality_fallback_post(self, nko_name: str, nko_activity: str, post_type: str, topic: str) -> List[str]:
        """Качественные резервные шаблоны до 250 символов"""
        
        if post_type == "fundraising":
            return [
                f"🐾 {nko_name} собирает средства на {topic}! Помогите нашим подопечным - каждое пожертвование важно для {nko_activity}. Поддержите доброе дело! ❤️\n\n#СборСредств #{nko_name.replace(' ', '')} #ПомощьЖивотным",
                
                f"🌟 {nko_name} обращается за помощью! {topic} Ваша поддержка нужна для {nko_activity}. Вместе мы сможем больше! 🙏\n\n#{nko_activity.replace(' ', '')} #{nko_name.replace(' ', '')} #Благотворительность"
            ]
        
        elif post_type == "thanks":
            return [
                f"🙏 {nko_name} благодарит за поддержку! {topic} Спасибо, что помогаете нам в {nko_activity}. Вы - наши герои! 💫\n\n#Благодарность #{nko_name.replace(' ', '')} #Спасибо",
                
                f"💕 {nko_name} говорит спасибо! {topic} Ваша помощь в {nko_activity} бесценна. Мы ценим каждого из вас! 🌟\n\n#Признательность #{nko_activity.replace(' ', '')} #Команда"
            ]
        
        elif post_type == "report":
            return [
                f"📊 {nko_name} отчитывается: {topic} Благодаря вам мы продолжаем {nko_activity}. Спасибо за доверие! 📈\n\n#Отчет #{nko_name.replace(' ', '')} #Результаты",
                
                f"✨ {nko_name} | Итоги: {topic} Наша работа по {nko_activity} приносит плоды. Вместе мы меняем мир! 🚀\n\n#Итоги #{nko_activity.replace(' ', '')} #Успех"
            ]
        
        elif post_type == "story":
            return [
                f"📖 {nko_name} делится историей: {topic} Наша деятельность {nko_activity} меняет жизни. Читайте и вдохновляйтесь! 💕\n\n#История #{nko_name.replace(' ', '')} #Вдохновение",
                
                f"❤️ История от {nko_name}: {topic} Благодаря {nko_activity} мы видим чудеса каждый день. Это мотивирует! ✨\n\n#ИсторияУспеха #{nko_activity.replace(' ', '')} #Добро"
            ]
        
        else:
            return [
                f"📢 {nko_name} сообщает: {topic} Мы продолжаем нашу деятельность по {nko_activity}. Следите за обновлениями! 🔔\n\n#Новости #{nko_name.replace(' ', '')} #Обновления",
                
                f"💡 {nko_name} информирует: {topic} Наша работа в сфере {nko_activity} важна для общества. Присоединяйтесь! 🤝\n\n#Информация #{nko_activity.replace(' ', '')} #Сообщество"
            ]