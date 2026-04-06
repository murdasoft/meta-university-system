# Qazaqdana OCR - Backend API

Панель администратора и API для Flutter приложения распознавания текста с изображений.

## Возможности

- 🔐 Аутентификация администратора через JWT
- 🌍 Поддержка трех языков: русский, казахский, английский
- 📸 Загрузка и распознавание текста с изображений
- 📊 Дашборд со статистикой
- 👥 Управление пользователями
- ⚙️ Настройки OCR системы
- 📱 REST API для Flutter приложения
- 💬 Чат и быстрые действия над распознанным текстом (OpenAI API, JWT)
- 📚 Автоматическая документация API (Swagger/ReDoc)

## Технологии

- Django 4.2
- Django REST Framework
- PostgreSQL
- EasyOCR
- OpenAI API (чат / быстрые действия по тексту OCR)
- JWT Authentication
- Swagger/OpenAPI

## Структура приложений

```
danadjango/
├── accounts/       # Аутентификация и управление пользователями
├── ocr/            # Распознавание текста OCR
├── dashboard/      # Статистика и дашборд
├── ai_assistant/   # Чат и quick actions над текстом (OpenAI)
└── danadjango/     # Настройки проекта
```

## Установка

Полная пошаговая инструкция для локальной машины (venv, PostgreSQL, `.env`, миграции, запуск): **`документация/00_ЛОКАЛЬНЫЙ_ЗАПУСК.md`**.

### 1. Клонирование и настройка окружения

```bash
cd /Users/daniyarmukhtarov/Desktop/project/qazaqdana/danadjango
source venv-danadjango/bin/activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка PostgreSQL

Убедитесь, что PostgreSQL запущен:

```bash
# Проверка статуса PostgreSQL
brew services list

# Если не запущен, запустите:
brew services start postgresql@14
```

Создайте базу данных:

```bash
# Войдите в PostgreSQL
psql postgres

# Создайте базу данных и пользователя
CREATE DATABASE qazaqdana_db;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'Asia/Almaty';
GRANT ALL PRIVILEGES ON DATABASE qazaqdana_db TO postgres;
\q
```

### 4. Настройка .env файла

Файл `.env` уже создан со следующими параметрами:

```
DB_NAME=qazaqdana_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

При необходимости измените параметры.

### 5. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Инициализация базовых данных

```bash
# Создание языков и настроек OCR
python manage.py init_ocr

# Создание администратора и тестового пользователя
python manage.py init_data
```

Будут созданы:
- Администратор: `admin` / `admin123`
- Тестовый пользователь: `testuser` / `test123`

### 7. Сборка статических файлов

```bash
python manage.py collectstatic --noinput
```

## Запуск сервера

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: http://localhost:8000

## Доступные URL

### Админ-панель
- **Панель администратора**: http://localhost:8000/admin/
  - Логин: `admin`
  - Пароль: `admin123`

### API Endpoints

#### Аутентификация
- `POST /api/accounts/token/` - Получить JWT токен
- `POST /api/accounts/token/refresh/` - Обновить JWT токен
- `GET /api/accounts/users/me/` - Информация о текущем пользователе
- `PUT /api/accounts/users/update_profile/` - Обновить профиль

#### OCR
- `GET /api/ocr/languages/` - Список поддерживаемых языков
- `GET /api/ocr/requests/` - Список OCR запросов
- `POST /api/ocr/requests/` - Создать OCR запрос (загрузить изображение)
- `GET /api/ocr/requests/{id}/` - Детали OCR запроса
- `POST /api/ocr/requests/{id}/reprocess/` - Повторно обработать изображение
- `GET /api/ocr/settings/` - Настройки OCR (только для админов)

#### Dashboard
- `GET /api/dashboard/` - Общая статистика
- `GET /api/dashboard/users_stats/` - Статистика пользователей
- `GET /api/dashboard/performance/` - Статистика производительности

#### Чат по распознанному тексту (AI)
Все запросы с заголовком `Authorization: Bearer <access>`.

- `POST /api/ai/chat/` — сообщение в чат (контекст — распознанный текст)
- `POST /api/ai/quick-action/` — быстрые действия (перевод, правка, кратко, объяснение)
- `GET /api/ai/history/` — список сессий чата
- `GET /api/ai/session/<uuid>/` — сообщения сессии
- `DELETE /api/ai/session/<uuid>/delete/` — удалить сессию
- `GET /api/ai/quota/` — квота запросов (лимиты по тарифу)

Для работы нужен **API-ключ OpenAI**, заведённый в настройках дашборда (тип ключа как для Vision/OCR — см. `документация/CHATGPT_INTEGRATION.md` и `AI_CHAT_BACKEND.md`).

Подробнее: **`документация/AI_CHAT_BACKEND.md`** (backend), **`документация/FLUTTER_AI_CHAT.md`** (Flutter).

### Документация API
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **OpenAPI JSON**: http://localhost:8000/swagger.json

## Использование API

### 1. Получение токена

```bash
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@qazaqdana.local",
    "role": "admin"
  }
}
```

### 2. Загрузка изображения для распознавания

```bash
curl -X POST http://localhost:8000/api/ocr/requests/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image=@/path/to/image.jpg" \
  -F "language=1"
```

### 3. Получение результатов распознавания

```bash
curl -X GET http://localhost:8000/api/ocr/requests/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Ответ:
```json
{
  "id": 1,
  "user": "admin",
  "image": "/media/ocr_images/2024/02/11/image.jpg",
  "language": 1,
  "language_name": "Русский",
  "recognized_text": "Распознанный текст...",
  "status": "completed",
  "confidence": 0.95,
  "processing_time": 2.34,
  "created_at": "2024-02-11T10:00:00Z"
}
```

## Для Flutter разработчиков

### Пример интеграции с Flutter

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';

class OCRService {
  final String baseUrl = 'http://localhost:8000/api';
  String? accessToken;

  // Авторизация
  Future<void> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/accounts/token/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      accessToken = data['access'];
    }
  }

  // Загрузка изображения для распознавания
  Future<Map<String, dynamic>> uploadImage(File imageFile, int languageId) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/ocr/requests/'),
    );
    
    request.headers['Authorization'] = 'Bearer $accessToken';
    request.files.add(await http.MultipartFile.fromPath('image', imageFile.path));
    request.fields['language'] = languageId.toString();
    
    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    
    return jsonDecode(responseData);
  }

  // Получение результата распознавания
  Future<Map<String, dynamic>> getOCRResult(int requestId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/ocr/requests/$requestId/'),
      headers: {'Authorization': 'Bearer $accessToken'},
    );
    
    return jsonDecode(response.body);
  }
}
```

## Модели данных

### CustomUser
- username (string)
- email (string)
- role (admin/user)
- phone_number (string, optional)
- avatar (image, optional)

### OCRRequest
- user (ForeignKey)
- image (ImageField)
- language (ForeignKey)
- recognized_text (text)
- status (pending/processing/completed/failed)
- confidence (float)
- processing_time (float)

### Language
- code (string: ru, kk, en)
- name (string)
- is_active (boolean)

## Разработка

### Создание новых миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

### Создание суперпользователя вручную

```bash
python manage.py createsuperuser
```

### Запуск тестов

```bash
python manage.py test
```

## Поддержка

При возникновении проблем:
1. Проверьте, что PostgreSQL запущен
2. Проверьте настройки в `.env` файле
3. Убедитесь, что все зависимости установлены
4. Проверьте логи: `python manage.py runserver`

## Лицензия

© 2026 Qazaqdana OCR. Все права защищены.
