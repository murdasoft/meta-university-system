# 🌐 API Документация Qazaq Dana

## 📋 Базовая информация

### Base URL
```
http://109.248.32.73
```

### Swagger/OpenAPI документация
```
http://109.248.32.73/swagger/
http://109.248.32.73/redoc/
```

### Формат ответов
Все API возвращают JSON

### Аутентификация
JWT (JSON Web Token) через заголовок `Authorization: Bearer <token>`

---

## 🔐 Аутентификация (Auth)

### 1. Получение токена (Login)

**Endpoint:** `POST /api/accounts/token/`

**Описание:** Получение JWT токена для авторизации

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response 200:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@meta-university.kz",
    "role": "admin",
    "full_name": "Administrator"
  }
}
```

**Пример (curl):**
```bash
curl -X POST http://109.248.32.73/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Обновление токена

**Endpoint:** `POST /api/accounts/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response 200:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 👥 Пользователи (Users)

### 1. Список пользователей

**Endpoint:** `GET /api/accounts/api/users/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@meta-university.kz",
    "role": "admin",
    "phone_number": "+7 777 123 4567",
    "is_active": true,
    "date_joined": "2026-02-11T04:42:00Z"
  }
]
```

### 2. Создание пользователя

**Endpoint:** `POST /api/accounts/api/users/`

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123",
  "role": "user",
  "phone_number": "+7 777 999 8888"
}
```

### 3. Детали пользователя

**Endpoint:** `GET /api/accounts/api/users/{id}/`

### 4. Обновление пользователя

**Endpoint:** `PUT /api/accounts/api/users/{id}/`

### 5. Удаление пользователя

**Endpoint:** `DELETE /api/accounts/api/users/{id}/`

---

## 📸 OCR (Распознавание текста)

### 1. Загрузка изображения для распознавания

**Endpoint:** `POST /api/ocr/requests/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
image: <file>
language: 1  (ID языка: 1-Русский, 2-Казахский, 3-Английский)
```

**Response 201:**
```json
{
  "id": 1,
  "user": 1,
  "image": "http://109.248.32.73/media/ocr_images/2026/02/11/image.jpg",
  "language": {
    "id": 1,
    "code": "ru",
    "name": "Русский"
  },
  "recognized_text": "Распознанный текст...",
  "status": "completed",
  "confidence": 95.5,
  "processing_time": 1.234,
  "created_at": "2026-02-11T04:45:00Z"
}
```

**Пример (curl):**
```bash
curl -X POST http://109.248.32.73/api/ocr/requests/ \
  -H "Authorization: Bearer <token>" \
  -F "image=@/path/to/image.jpg" \
  -F "language=1"
```

**Пример (Python):**
```python
import requests

url = "http://109.248.32.73/api/ocr/requests/"
headers = {"Authorization": "Bearer <token>"}
files = {"image": open("image.jpg", "rb")}
data = {"language": 1}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### 2. Список OCR запросов

**Endpoint:** `GET /api/ocr/requests/`

**Query Parameters:**
- `status` - фильтр по статусу (pending, processing, completed, failed)
- `language` - фильтр по языку (ID)
- `ordering` - сортировка (-created_at, confidence)

**Response 200:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "language": {"id": 1, "name": "Русский"},
      "status": "completed",
      "recognized_text": "Текст...",
      "confidence": 95.5,
      "created_at": "2026-02-11T04:45:00Z"
    }
  ]
}
```

### 3. Детали OCR запроса

**Endpoint:** `GET /api/ocr/requests/{id}/`

### 4. Доступные языки

**Endpoint:** `GET /api/ocr/languages/`

**Response 200:**
```json
[
  {
    "id": 1,
    "code": "ru",
    "name": "Русский",
    "is_active": true
  },
  {
    "id": 2,
    "code": "kk",
    "name": "Қазақша",
    "is_active": true
  },
  {
    "id": 3,
    "code": "en",
    "name": "English",
    "is_active": true
  }
]
```

### 5. Настройки OCR

**Endpoint:** `GET /api/ocr/settings/`

**Response 200:**
```json
[
  {
    "id": 1,
    "key": "max_image_size",
    "value": "10485760",
    "description": "Максимальный размер изображения (10 MB)"
  },
  {
    "id": 2,
    "key": "supported_formats",
    "value": "jpg,jpeg,png,bmp,tiff",
    "description": "Поддерживаемые форматы изображений"
  }
]
```

---

## 📊 Dashboard (Статистика)

### 1. Общая статистика

**Endpoint:** `GET /api/dashboard/api/`

**Response 200:**
```json
{
  "total_users": 5,
  "active_users": 4,
  "total_requests": 150,
  "recent_requests": 45,
  "requests_stats": {
    "total": 150,
    "completed": 140,
    "failed": 5,
    "processing": 2,
    "avg_time": 1.234,
    "avg_confidence": 94.5
  },
  "languages_stats": [
    {"language__name": "Русский", "count": 80},
    {"language__name": "Қазақша", "count": 50},
    {"language__name": "English", "count": 20}
  ],
  "daily_stats": [
    {
      "date": "2026-02-11",
      "total": 25,
      "completed": 23,
      "failed": 2
    }
  ]
}
```

### 2. Статистика пользователей

**Endpoint:** `GET /api/dashboard/api/users_stats/`

**Response 200:**
```json
{
  "top_users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@meta-university.kz",
      "requests_count": 45,
      "date_joined": "2026-02-11T04:42:00Z"
    }
  ]
}
```

### 3. Производительность

**Endpoint:** `GET /api/dashboard/api/performance/`

**Response 200:**
```json
{
  "avg_processing_time": 1.234,
  "avg_confidence": 94.5
}
```

---

## 📱 Интеграция для Flutter приложения

### Полный workflow для Flutter

#### 1. Авторизация

```dart
// 1. Получение токена
final response = await http.post(
  Uri.parse('http://109.248.32.73/api/accounts/token/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'username': 'user',
    'password': 'password',
  }),
);

final data = jsonDecode(response.body);
String accessToken = data['access'];
String refreshToken = data['refresh'];
```

#### 2. Загрузка изображения для OCR

```dart
// 2. Отправка изображения
var request = http.MultipartRequest(
  'POST',
  Uri.parse('http://109.248.32.73/api/ocr/requests/'),
);

request.headers['Authorization'] = 'Bearer $accessToken';
request.files.add(await http.MultipartFile.fromPath('image', imagePath));
request.fields['language'] = '1'; // 1-Русский, 2-Казахский, 3-Английский

var streamedResponse = await request.send();
var response = await http.Response.fromStream(streamedResponse);
var result = jsonDecode(response.body);

print('Распознанный текст: ${result['recognized_text']}');
print('Точность: ${result['confidence']}%');
```

#### 3. Проверка истории запросов

```dart
// 3. Получение списка запросов
final response = await http.get(
  Uri.parse('http://109.248.32.73/api/ocr/requests/'),
  headers: {'Authorization': 'Bearer $accessToken'},
);

List requests = jsonDecode(response.body)['results'];
```

---

## 🔧 Коды ответов

| Код | Описание |
|-----|----------|
| 200 | OK - Успешный запрос |
| 201 | Created - Ресурс создан |
| 204 | No Content - Успешно удалено |
| 400 | Bad Request - Неверные данные |
| 401 | Unauthorized - Не авторизован |
| 403 | Forbidden - Нет прав доступа |
| 404 | Not Found - Ресурс не найден |
| 500 | Internal Server Error - Ошибка сервера |

---

## 🧪 Тестирование API

### Postman Collection

Импортируйте в Postman:

```json
{
  "info": {
    "name": "Qazaq Dana API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://109.248.32.73",
      "type": "string"
    },
    {
      "key": "access_token",
      "value": "",
      "type": "string"
    }
  ]
}
```

### Примеры curl

```bash
# 1. Login
curl -X POST http://109.248.32.73/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Получить список пользователей
curl -X GET http://109.248.32.73/api/accounts/api/users/ \
  -H "Authorization: Bearer <token>"

# 3. Загрузить изображение для OCR
curl -X POST http://109.248.32.73/api/ocr/requests/ \
  -H "Authorization: Bearer <token>" \
  -F "image=@image.jpg" \
  -F "language=1"

# 4. Получить статистику
curl -X GET http://109.248.32.73/api/dashboard/api/ \
  -H "Authorization: Bearer <token>"
```

---

**См. также:** `04_БАЗА_ДАННЫХ.md`
