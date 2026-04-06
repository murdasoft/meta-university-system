import time
import logging
import base64
import os
from PIL import Image
from io import BytesIO
from django.conf import settings
from decouple import config

logger = logging.getLogger(__name__)

# Google Vision API через REST (не требует установки библиотеки)
try:
    import requests
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logger.warning("Библиотека requests не установлена. Установите: pip install requests")

# Tesseract (fallback)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    # Установка пути к tesseract
    import shutil
    tesseract_cmd = shutil.which('tesseract')
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        # Попробуем стандартные пути
        for path in ['/usr/bin/tesseract', '/usr/local/bin/tesseract']:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
except ImportError:
    pytesseract = None
    TESSERACT_AVAILABLE = False
    logger.warning("Pytesseract не установлен. Установите: pip install pytesseract")


class OCRService:
    """Сервис для распознавания текста с изображений"""
    
    @classmethod
    def _get_openai_api_key(cls):
        """Получить API ключ OpenAI из базы данных"""
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
            logger.warning(f"Не удалось получить OpenAI API ключ из БД: {e}")
            return None
    
    @classmethod
    def _get_google_vision_api_key(cls):
        """Получить API ключ Google Vision из базы данных или использовать дефолтный"""
        try:
            from dashboard.models import APIKey
            api_key_obj = APIKey.objects.filter(
                key_type='google_vision',
                is_active=True
            ).first()
            
            if api_key_obj and api_key_obj.api_key:
                return api_key_obj.api_key.strip()
        except Exception as db_error:
            logger.warning(f"Не удалось получить ключ из БД: {db_error}")
        
        # Fallback: из .env или дефолтный ключ
        return config('GOOGLE_VISION_API_KEY', default='AIzaSyD0FPltRCTqaIUjlHo8p2TsrS1XgoJvnkg')
    
    @classmethod
    def recognize_with_google_vision(cls, image_content, language_code='ru'):
        """
        Распознавание текста через Google Vision API (REST API с простым ключом)
        
        Args:
            image_content: bytes или base64 строка изображения
            language_code: код языка (ru, kk, en)
        
        Returns:
            dict: результат распознавания
        """
        start_time = time.time()
        
        api_key = cls._get_google_vision_api_key()
        if not api_key:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'processing_time': 0.0,
                'error': 'Google Vision API ключ не настроен. Добавьте ключ в настройках.'
            }
        
        try:
            import requests
            
            # Подготовка изображения
            if isinstance(image_content, str):
                # Если base64 строка
                image_base64 = image_content
            else:
                # Конвертируем bytes в base64
                image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Маппинг языков для Google Vision
            language_hints = {
                'ru': ['ru'],
                'kk': ['kk', 'ru'],  # Казахский + русский fallback
                'en': ['en'],
            }
            hints = language_hints.get(language_code, ['ru'])
            
            # Вызов Google Vision API через REST
            url = f'https://vision.googleapis.com/v1/images:annotate?key={api_key}'
            
            payload = {
                'requests': [{
                    'image': {
                        'content': image_base64
                    },
                    'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }],
                    'imageContext': {
                        'languageHints': hints
                    }
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Извлечение текста
            if 'responses' in result and len(result['responses']) > 0:
                response_data = result['responses'][0]
                
                if 'textAnnotations' in response_data and len(response_data['textAnnotations']) > 0:
                    full_text = response_data['textAnnotations'][0].get('description', '')
                    
                    # Расчет уверенности (если доступно)
                    if len(response_data['textAnnotations']) > 1:
                        confidences = []
                        for annotation in response_data['textAnnotations'][1:]:
                            if 'confidence' in annotation:
                                confidences.append(annotation['confidence'])
                        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.95
                    else:
                        avg_confidence = 0.95  # Дефолтная уверенность
                else:
                    full_text = ''
                    avg_confidence = 0.0
            else:
                full_text = ''
                avg_confidence = 0.0
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'text': full_text.strip(),
                'confidence': avg_confidence,
                'processing_time': processing_time,
                'language': language_code,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка Google Vision API (HTTP): {str(e)}")
            processing_time = time.time() - start_time
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(e))
                except:
                    error_msg = f"HTTP {e.response.status_code}: {str(e)}"
            # При 403 или других ошибках API возвращаем success=False для fallback
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'processing_time': processing_time,
                'error': f'Google Vision API ошибка: {error_msg}',
                'use_fallback': True  # Флаг для использования fallback
            }
        except Exception as e:
            logger.error(f"Ошибка Google Vision API: {str(e)}")
            processing_time = time.time() - start_time
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'processing_time': processing_time,
                'error': str(e)
            }
    
    @classmethod
    def recognize_with_chatgpt(cls, image_content, language_code='ru'):
        """
        Распознавание текста через ChatGPT-4 Vision API
        
        Args:
            image_content: base64 строка или bytes изображения
            language_code: код языка (ru, kk, en)
        
        Returns:
            dict: результат распознавания
        """
        start_time = time.time()
        
        # Получаем API ключ
        api_key = cls._get_openai_api_key()
        
        if not api_key:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'processing_time': 0.0,
                'error': 'OpenAI API ключ не настроен. Добавьте ключ в настройках.'
            }
        
        try:
            import requests
            
            # Подготовка изображения
            if isinstance(image_content, str):
                image_base64 = image_content
            else:
                image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Промпт в зависимости от языка
            language_prompts = {
                'ru': 'Распознай весь текст на этом изображении на русском языке. Верни только текст, без комментариев.',
                'kk': 'Распознай весь текст на этом изображении на казахском языке. Верни только текст, без комментариев.',
                'en': 'Recognize all text in this image in English. Return only the text, no comments.',
            }
            prompt = language_prompts.get(language_code, language_prompts['ru'])
            
            # Вызов OpenAI API
            url = 'https://api.openai.com/v1/chat/completions'
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            payload = {
                'model': 'gpt-4o',  # или gpt-4-vision-preview
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': prompt
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{image_base64}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 1000
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Извлечение текста
            if 'choices' in result and len(result['choices']) > 0:
                full_text = result['choices'][0]['message']['content'].strip()
                # ChatGPT обычно очень уверен, если смог распознать
                avg_confidence = 0.95 if full_text else 0.0
            else:
                full_text = ''
                avg_confidence = 0.0
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'text': full_text,
                'confidence': avg_confidence,
                'processing_time': processing_time,
                'language': language_code,
                'error': None,
                'engine': 'chatgpt-4-vision'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка ChatGPT-4 Vision API (HTTP): {str(e)}")
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
                'text': '',
                'confidence': 0.0,
                'processing_time': processing_time,
                'error': f'ChatGPT-4 Vision API ошибка: {error_msg}',
                'use_fallback': True
            }
        except Exception as e:
            logger.error(f"Ошибка ChatGPT-4 Vision API: {str(e)}")
            processing_time = time.time() - start_time
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'processing_time': processing_time,
                'error': str(e)
            }
    
    @classmethod
    def recognize_with_tesseract(cls, image_path, language_code='ru'):
        """
        Распознавание текста через Tesseract (fallback)
        
        Args:
            image_path: путь к изображению
            language_code: код языка (ru, kk, en)
        
        Returns:
            dict: результат распознавания
        """
        start_time = time.time()
        
        if not TESSERACT_AVAILABLE:
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'processing_time': 0.0,
                'error': 'Tesseract не установлен'
            }
        
        try:
            img = Image.open(image_path)
            
            language_map = {
                'ru': 'rus',
                'kk': 'kaz',  # Казахский язык теперь доступен
                'en': 'eng',
            }
            
            tesseract_lang = language_map.get(language_code, 'rus')
            
            # Проверка доступности языка
            try:
                available_langs = pytesseract.get_languages()
                if tesseract_lang not in available_langs:
                    logger.warning(f"Язык {tesseract_lang} не доступен, используем rus")
                    tesseract_lang = 'rus' if tesseract_lang != 'eng' else 'eng'
            except Exception as e:
                logger.warning(f"Не удалось проверить доступные языки: {e}")
            
            data = pytesseract.image_to_data(
                img,
                lang=tesseract_lang,
                output_type=pytesseract.Output.DICT
            )
            
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
            full_text = pytesseract.image_to_string(img, lang=tesseract_lang)
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'text': full_text.strip(),
                'confidence': avg_confidence,
                'processing_time': processing_time,
                'language': language_code,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Ошибка Tesseract: {str(e)}")
            processing_time = time.time() - start_time
            return {
                'success': False,
                'text': '',
                'confidence': 0.0,
                'processing_time': processing_time,
                'error': str(e)
            }
    
    @classmethod
    def recognize_text(cls, image_content, language_code='ru', use_google_vision=True):
        """
        Распознавание текста (основной метод)
        
        Args:
            image_content: base64 строка (для Google Vision) или bytes/путь к файлу (для Tesseract)
            language_code: код языка (ru, kk, en)
            use_google_vision: использовать Google Vision (True) или Tesseract (False)
        
        Returns:
            dict: результат распознавания
        """
        # Подготовка временного файла для Tesseract (если нужен fallback)
        temp_file_path = None
        import tempfile
        import os
        
        try:
            # Конвертируем входные данные в нужный формат
            if isinstance(image_content, str):
                # Проверяем, это путь к файлу или base64
                if os.path.exists(image_content):
                    # Путь к файлу - используем напрямую для Tesseract
                    temp_file_path = image_content
                    # Читаем файл для Google Vision API
                    try:
                        with open(image_content, 'rb') as img_file:
                            image_bytes = img_file.read()
                            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    except Exception as e:
                        logger.error(f"Не удалось прочитать файл {image_content}: {e}")
                        image_base64 = None
                else:
                    # Base64 строка
                    image_base64 = image_content
                    # Подготавливаем файл для Tesseract fallback
                    try:
                        image_bytes = base64.b64decode(image_content)
                        # Проверяем, что это валидное изображение
                        from PIL import Image
                        from io import BytesIO
                        img = Image.open(BytesIO(image_bytes))
                        # Конвертируем в RGB если нужно
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        # Сохраняем во временный файл
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                            img.save(tmp, format='JPEG')
                            temp_file_path = tmp.name
                        logger.info(f"✅ Создан временный файл: {temp_file_path}")
                    except Exception as e:
                        logger.error(f"❌ Не удалось декодировать base64 или создать изображение: {e}")
                        temp_file_path = None
            elif isinstance(image_content, bytes):
                # Bytes - конвертируем в base64 для Google Vision
                image_base64 = base64.b64encode(image_content).decode('utf-8')
                # Подготавливаем файл для Tesseract fallback
                try:
                    from PIL import Image
                    from io import BytesIO
                    img = Image.open(BytesIO(image_content))
                    # Конвертируем в RGB если нужно
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                        img.save(tmp, format='JPEG')
                        temp_file_path = tmp.name
                except Exception as e:
                    logger.warning(f"Не удалось создать изображение из bytes: {e}")
                    temp_file_path = None
            else:
                image_base64 = None
                temp_file_path = None
            
            # Гибридный подход: Google Vision → ChatGPT-4 → Tesseract
            
            # 1. Пробуем Google Vision сначала (быстро и дёшево)
            if use_google_vision and GOOGLE_VISION_AVAILABLE and image_base64:
                result = cls.recognize_with_google_vision(image_base64, language_code)
                
                # Если успешно и confidence высокий - возвращаем результат
                if result['success'] and result.get('text', '').strip() and result.get('confidence', 0) >= 0.80:
                    logger.info(f"✅ Google Vision: успешно (confidence: {result.get('confidence')})")
                    return result
                
                # Если Google Vision вернул результат с низким confidence или пустой текст
                if result['success'] and result.get('confidence', 0) < 0.80:
                    logger.warning(f"⚠️ Google Vision: низкий confidence ({result.get('confidence')}), пробуем ChatGPT-4")
                elif result.get('error'):
                    logger.warning(f"❌ Google Vision ошибка: {result.get('error')}, пробуем ChatGPT-4")
                elif not result.get('text', '').strip():
                    logger.info("⚠️ Google Vision вернул пустой текст, пробуем ChatGPT-4")
                
                # 2. Пробуем ChatGPT-4 Vision (точнее, но дороже)
                chatgpt_result = cls.recognize_with_chatgpt(image_base64, language_code)
                if chatgpt_result['success'] and chatgpt_result.get('text', '').strip():
                    logger.info(f"✅ ChatGPT-4 Vision: успешно (confidence: {chatgpt_result.get('confidence')})")
                    return chatgpt_result
                else:
                    logger.warning(f"❌ ChatGPT-4 Vision не сработал, используем Tesseract fallback")
            
            # Fallback на Tesseract
            if TESSERACT_AVAILABLE and temp_file_path:
                # Проверяем, что это не base64 строка, а путь к файлу
                if not temp_file_path.startswith('/') and len(temp_file_path) > 200:
                    # Это base64 строка, а не путь к файлу - ошибка в логике
                    logger.error(f"temp_file_path содержит base64 вместо пути к файлу (первые 50 символов): {temp_file_path[:50]}")
                    return {
                        'success': False,
                        'text': '',
                        'confidence': 0.0,
                        'processing_time': 0.0,
                        'error': 'Tesseract fallback: временный файл не был создан правильно (base64 вместо пути)'
                    }
                
                if os.path.exists(temp_file_path):
                    logger.info(f"Используем Tesseract fallback для {temp_file_path}")
                    result = cls.recognize_with_tesseract(temp_file_path, language_code)
                    return result
                else:
                    logger.error(f"Tesseract fallback: файл не существует: {temp_file_path}")
                    return {
                        'success': False,
                        'text': '',
                        'confidence': 0.0,
                        'processing_time': 0.0,
                        'error': f'Tesseract fallback: временный файл не существует: {temp_file_path}'
                    }
            else:
                # Детальная ошибка для отладки
                error_details = []
                if not TESSERACT_AVAILABLE:
                    error_details.append("Tesseract не установлен")
                if not temp_file_path:
                    error_details.append("временный файл не создан")
                
                error_msg = f"Tesseract fallback недоступен: {', '.join(error_details)}"
                logger.error(error_msg)
                
                return {
                    'success': False,
                    'text': '',
                    'confidence': 0.0,
                    'processing_time': 0.0,
                    'error': error_msg
                }
        finally:
            # Удаляем временный файл если он был создан
            if temp_file_path and temp_file_path != image_content and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
    
    @classmethod
    def process_image(cls, image_path, language_code='ru'):
        """
        Обработать изображение (старый метод для совместимости)
        """
        return cls.recognize_text(image_path, language_code, use_google_vision=True)
