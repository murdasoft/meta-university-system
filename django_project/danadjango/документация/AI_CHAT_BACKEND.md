# 🤖 AI Чат - Документация Backend

## Обзор

Приложение Django `ai_assistant` добавляет чат и быстрые действия над распознанным текстом. Запросы к языковой модели идут через OpenAI API (в продакшене используется линейка моделей вроде `gpt-4o-mini`; точное имя задаётся в коде/настройках).

---

## Приложение `ai_assistant`

### Структура приложения

```
ai_assistant/
├── __init__.py
├── apps.py
├── models.py           # Модели: ChatSession, ChatMessage, AIUsageQuota
├── admin.py            # Админка для управления чатами и квотами
├── serializers.py      # Сериализаторы для API
├── views.py            # API views
├── urls.py             # URL маршруты
├── services.py         # Логика работы с OpenAI API
└── migrations/
    └── 0001_initial.py
```

---

## 📊 Модели данных

### 1. `ChatSession` - Сессия чата
```python
class ChatSession(models.Model):
    id = UUIDField()  # UUID для безопасности
    user = ForeignKey(User)
    recognition_text = TextField()  # Контекст из OCR
    created_at = DateTimeField()
    updated_at = DateTimeField()
```

### 2. `ChatMessage` - Сообщение в чате
```python
class ChatMessage(models.Model):
    id = UUIDField()
    session = ForeignKey(ChatSession)
    role = CharField()  # 'user' или 'assistant'
    content = TextField()
    created_at = DateTimeField()
```

### 3. `AIUsageQuota` — квота запросов
```python
class AIUsageQuota(models.Model):
    user = OneToOneField(User)
    daily_questions_used = IntegerField()
    last_reset_date = DateField()
    total_questions_asked = IntegerField()
    
    # Методы:
    def reset_if_needed()  # Сброс счётчика в новый день
    def can_ask_question()  # Проверка лимита
    def increment_usage()  # Увеличение счётчика
```

**Лимиты:**
- Free пользователи: 5 вопросов/день
- Premium пользователи: unlimited

---

## 🔌 API Эндпоинты

### 1. `POST /api/ai/chat/` - Отправить сообщение
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    # Проверка квоты
    # Создание/получение сессии
    # Сохранение сообщения пользователя
    # Отправка в ChatGPT
    # Сохранение ответа AI
    # Увеличение счётчика
```

### 2. `POST /api/ai/quick-action/` - Быстрые действия
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_action_view(request):
    # Проверка квоты
    # Выполнение действия (translate, correct, summarize, explain)
    # Увеличение счётчика
```

### 3. `GET /api/ai/history/` - История чатов
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history_view(request):
    # Возвращает все сессии пользователя с сообщениями
```

### 4. `GET /api/ai/session/{session_id}/` - Получить сессию
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_session_view(request, session_id):
    # Возвращает конкретную сессию с сообщениями
```

### 5. `DELETE /api/ai/session/{session_id}/delete/` - Удалить сессию
```python
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat_session_view(request, session_id):
    # Удаляет сессию и все её сообщения
```

### 6. `GET /api/ai/quota/` - Проверить квоту
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_quota_view(request):
    # Возвращает информацию о квоте пользователя
```

---

## 🧠 Сервис `AIAssistantService`

### Метод `chat()`
```python
@classmethod
def chat(cls, messages, recognition_text=None, language='ru'):
    """
    Отправляет сообщения в ChatGPT-4o-mini
    
    Args:
        messages: [{"role": "user", "content": "текст"}]
        recognition_text: контекст из OCR
        language: ru, kk, en
    
    Returns:
        {
            'success': bool,
            'response': str,
            'processing_time': float,
            'error': str or None
        }
    """
```

**Особенности:**
- Использует модель `gpt-4o-mini` (дешевле чем gpt-4o)
- Системный промпт адаптируется под язык
- Контекст (recognition_text) добавляется в системный промпт
- История последних 10 сообщений передаётся для контекста
- Timeout: 30 секунд
- Max tokens: 500

### Метод `quick_action()`
```python
@classmethod
def quick_action(cls, action, text, language='ru'):
    """
    Быстрые действия с текстом
    
    Actions:
        - translate_ru, translate_kk, translate_en
        - correct (исправление ошибок)
        - summarize (краткое резюме)
        - explain (объяснение текста)
    """
```

---

## 🔧 Изменения в существующих файлах

### 1. `danadjango/settings.py`
```python
INSTALLED_APPS = [
    # ...
    'ai_assistant',  # ДОБАВЛЕНО
]
```

### 2. `danadjango/urls.py`
```python
urlpatterns = [
    # ...
    path('api/ai/', include('ai_assistant.urls')),  # ДОБАВЛЕНО
]
```

---

## 🔑 Требования

### 1. OpenAI API ключ
Должен быть добавлен в админ-панели:
- Тип: "OpenAI (ChatGPT-4 Vision)"
- Активен: ✅
- Получить ключ: https://platform.openai.com/api-keys

### 2. Python пакеты
Все необходимые пакеты уже установлены:
- `requests` - для HTTP запросов к OpenAI API
- `djangorestframework` - для API
- `rest_framework_simplejwt` - для авторизации

---

## 💰 Стоимость использования

### ChatGPT-4o-mini цены (на март 2026):
- **Input:** $0.15 / 1M tokens
- **Output:** $0.60 / 1M tokens

### Примерная стоимость:
- 1 вопрос ≈ 200 tokens input + 150 tokens output
- 1 вопрос ≈ $0.00012 (≈ 0.012 ₸)
- 1000 вопросов ≈ $0.12 (≈ 12 ₸)

Ориентир для оценки расходов на API (актуальные тарифы смотреть на сайте OpenAI).

---

## 📈 Мониторинг

### Django Admin
Доступ к статистике через админку:
- http://109.248.32.73/admin/ai_assistant/chatsession/
- http://109.248.32.73/admin/ai_assistant/chatmessage/
- http://109.248.32.73/admin/ai_assistant/aiusagequota/

### Метрики для отслеживания:
1. Количество вопросов в день
2. Средняя длина сессий
3. Популярные быстрые действия
4. Процент пользователей, достигших лимита

---

## 🧪 Тестирование

### Swagger UI
http://109.248.32.73/swagger/

Все новые эндпоинты автоматически добавлены в Swagger документацию.

### Пример curl запроса:
```bash
# Отправить сообщение
curl -X POST http://109.248.32.73/api/ai/chat/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Переведи на русский",
    "recognition_text": "Hello world",
    "language": "ru"
  }'

# Проверить квоту
curl -X GET http://109.248.32.73/api/ai/quota/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔒 Безопасность

### 1. Авторизация
- Все эндпоинты требуют JWT токен
- Пользователь видит только свои чаты

### 2. Лимиты
- Free: 5 вопросов/день (защита от злоупотреблений)
- Premium: unlimited (для платящих пользователей)

### 3. API ключ
- Хранится в базе данных (зашифрован)
- Не передаётся клиенту
- Используется только на backend

---

## 🚀 Деплой

### Что было сделано:
1. ✅ Создано приложение `ai_assistant`
2. ✅ Добавлено в `INSTALLED_APPS`
3. ✅ Добавлены URL маршруты
4. ✅ Загружено на сервер (109.248.32.73)
5. ✅ Выполнены миграции
6. ✅ Перезапущен gunicorn

### Статус сервиса:
```bash
systemctl status qazaqdana
# ● qazaqdana.service - Qazaq Dana Django Application
#      Active: active (running)
```

---

## 📝 TODO (опционально)

### Будущие улучшения:
1. **Аналитика:**
   - Dashboard с графиками использования
   - Топ вопросов пользователей
   - Средняя длина ответов

2. **Функционал:**
   - Голосовой ввод/вывод
   - Экспорт чатов в PDF
   - Поделиться чатом

3. **Оптимизация:**
   - Кэширование частых запросов
   - Streaming ответов (SSE)
   - Batch обработка для быстрых действий

---

## Связанные материалы

Описание HTTP API для мобильного клиента и примеры на Dart: `FLUTTER_AI_CHAT.md`.
