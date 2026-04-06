import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


class AIAssistantService:
    """Сервис для работы с AI ассистентом (ChatGPT)"""
    
    @classmethod
    def _get_openai_api_key(cls):
        """Получить OpenAI API ключ из базы данных"""
        try:
            from dashboard.models import APIKey
            api_key_obj = APIKey.objects.filter(
                key_type='openai',
                is_active=True
            ).first()
            
            if api_key_obj:
                return api_key_obj.api_key
            return None
        except Exception as e:
            logger.warning(f"Не удалось получить OpenAI API ключ: {e}")
            return None
    
    @classmethod
    def chat(cls, messages, recognition_text=None, language='ru'):
        """
        Отправить сообщения в ChatGPT и получить ответ
        
        Args:
            messages: список сообщений [{"role": "user", "content": "текст"}]
            recognition_text: распознанный текст (контекст)
            language: язык ответа (ru, kk, en)
        
        Returns:
            dict: {
                'success': bool,
                'response': str,
                'processing_time': float,
                'error': str or None
            }
        """
        start_time = time.time()
        
        # Получаем API ключ
        api_key = cls._get_openai_api_key()
        
        if not api_key:
            return {
                'success': False,
                'response': '',
                'processing_time': 0.0,
                'error': 'OpenAI API ключ не настроен. Попросите администратора добавить ключ в настройках.'
            }
        
        try:
            import requests
            
            # Системный промпт в зависимости от языка
            system_prompts = {
                'ru': 'Ты умный помощник для работы с текстом. Помогаешь пользователям переводить, исправлять, объяснять и анализировать распознанный текст. Отвечай кратко и по делу на русском языке.',
                'kk': 'Сіз мәтінмен жұмыс істеуге арналған ақылды көмекшісіз. Пайдаланушыларға аударуға, түзетуге, түсіндіруге және танылған мәтінді талдауға көмектесесіз. Қазақ тілінде қысқа және нақты жауап беріңіз.',
                'en': 'You are a smart assistant for working with text. You help users translate, correct, explain and analyze recognized text. Answer briefly and to the point in English.',
            }
            
            system_prompt = system_prompts.get(language, system_prompts['ru'])
            
            # Если есть распознанный текст, добавляем его в контекст
            if recognition_text:
                system_prompt += f'\n\nКонтекст (распознанный текст):\n"""\n{recognition_text}\n"""'
            
            # Формируем полный список сообщений
            full_messages = [
                {'role': 'system', 'content': system_prompt}
            ]
            full_messages.extend(messages)
            
            # Вызов OpenAI API
            url = 'https://api.openai.com/v1/chat/completions'
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            payload = {
                'model': 'gpt-4o-mini',  # Более дешёвая модель для чата
                'messages': full_messages,
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Извлечение ответа
            if 'choices' in result and len(result['choices']) > 0:
                assistant_message = result['choices'][0]['message']['content'].strip()
            else:
                assistant_message = ''
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'response': assistant_message,
                'processing_time': processing_time,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка OpenAI API (HTTP): {str(e)}")
            processing_time = time.time() - start_time
            error_msg = str(e)
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(e))
                except:
                    error_msg = f"HTTP {e.response.status_code}: {str(e)}"
            
            return {
                'success': False,
                'response': '',
                'processing_time': processing_time,
                'error': f'OpenAI API ошибка: {error_msg}'
            }
        except Exception as e:
            logger.error(f"Ошибка AI ассистента: {str(e)}")
            processing_time = time.time() - start_time
            return {
                'success': False,
                'response': '',
                'processing_time': processing_time,
                'error': str(e)
            }
    
    @classmethod
    def quick_action(cls, action, text, language='ru'):
        """
        Быстрые действия с текстом
        
        Args:
            action: тип действия (translate, correct, summarize, explain)
            text: текст для обработки
            language: целевой язык
        
        Returns:
            dict: результат обработки
        """
        action_prompts = {
            'translate_ru': f'Переведи этот текст на русский язык:\n\n{text}',
            'translate_kk': f'Переведи этот текст на казахский язык:\n\n{text}',
            'translate_en': f'Translate this text to English:\n\n{text}',
            'correct': f'Исправь ошибки в этом тексте и верни исправленную версию:\n\n{text}',
            'summarize': f'Кратко резюмируй этот текст (2-3 предложения):\n\n{text}',
            'explain': f'Объясни простыми словами, что означает этот текст:\n\n{text}',
        }
        
        prompt = action_prompts.get(action, f'{action}:\n\n{text}')
        
        messages = [
            {'role': 'user', 'content': prompt}
        ]
        
        return cls.chat(messages, recognition_text=None, language=language)
