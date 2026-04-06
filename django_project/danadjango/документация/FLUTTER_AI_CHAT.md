# 🤖 AI Ассистент - Инструкция для Flutter разработчика

## Обзор

Через API доступны чат и быстрые действия над распознанным текстом (бэкенд ходит в OpenAI). Пользователь в приложении может:
- Задавать вопросы о распознанном тексте
- Переводить текст на другие языки
- Исправлять ошибки в тексте
- Получать краткое резюме текста
- Объяснять значение текста

## 🎯 Основные возможности

### 1. **AI Чат** (основной функционал)
- Полноценный чат с контекстом распознанного текста
- История сообщений сохраняется в сессиях
- Поддержка русского, казахского и английского языков
- Лимиты: 5 вопросов/день для Free, unlimited для Premium

### 2. **Быстрые действия**
- Перевод на русский/казахский/английский
- Исправление ошибок
- Краткое резюме
- Объяснение текста

### 3. **История чатов**
- Просмотр всех сессий чата
- Продолжение существующих чатов
- Удаление старых чатов

### 4. **Квота использования**
- Проверка оставшихся вопросов
- Статистика использования

---

## 🔌 API Эндпоинты

### 1. POST `/api/ai/chat/` - Отправить сообщение в чат

**Требуется авторизация:** ✅ (JWT Token)

**Request:**
```json
{
  "message": "Переведи этот текст на русский",
  "session_id": "uuid" // опционально, если продолжаем существующий чат
  "recognition_text": "Hello world", // опционально, контекст
  "language": "ru" // ru, kk, en
}
```

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Привет мир",
  "processing_time": 1.234,
  "remaining_questions": 4 // -1 для Premium (unlimited)
}
```

**Response (403) - Лимит исчерпан:**
```json
{
  "error": "Достигнут дневной лимит (5 вопросов). Обновитесь до Premium для unlimited доступа.",
  "remaining_questions": 0,
  "is_premium": false
}
```

---

### 2. POST `/api/ai/quick-action/` - Быстрые действия

**Требуется авторизация:** ✅ (JWT Token)

**Request:**
```json
{
  "action": "translate_ru", // translate_ru, translate_kk, translate_en, correct, summarize, explain
  "text": "Hello world",
  "language": "ru"
}
```

**Response (200):**
```json
{
  "result": "Привет мир",
  "processing_time": 0.856
}
```

---

### 3. GET `/api/ai/history/` - История чатов

**Требуется авторизация:** ✅ (JWT Token)

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "recognition_text": "Hello world",
    "created_at": "2026-03-10T12:00:00Z",
    "updated_at": "2026-03-10T12:05:00Z",
    "message_count": 4,
    "messages": [
      {
        "id": "uuid",
        "role": "user",
        "content": "Переведи на русский",
        "created_at": "2026-03-10T12:00:00Z"
      },
      {
        "id": "uuid",
        "role": "assistant",
        "content": "Привет мир",
        "created_at": "2026-03-10T12:00:05Z"
      }
    ]
  }
]
```

---

### 4. GET `/api/ai/session/{session_id}/` - Получить конкретную сессию

**Требуется авторизация:** ✅ (JWT Token)

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "recognition_text": "Hello world",
  "created_at": "2026-03-10T12:00:00Z",
  "updated_at": "2026-03-10T12:05:00Z",
  "message_count": 4,
  "messages": [...]
}
```

---

### 5. DELETE `/api/ai/session/{session_id}/delete/` - Удалить сессию

**Требуется авторизация:** ✅ (JWT Token)

**Response (204):** Успешно удалено

---

### 6. GET `/api/ai/quota/` - Проверить квоту

**Требуется авторизация:** ✅ (JWT Token)

**Response (200):**
```json
{
  "daily_questions_used": 3,
  "total_questions_asked": 127,
  "last_reset_date": "2026-03-10",
  "can_ask": true,
  "remaining_questions": 2, // -1 для Premium (unlimited)
  "is_premium": false
}
```

---

## 📱 Пример реализации во Flutter

### 1. Модели данных

```dart
// lib/models/ai_chat.dart

class ChatMessage {
  final String id;
  final String role; // 'user' или 'assistant'
  final String content;
  final DateTime createdAt;

  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.createdAt,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      role: json['role'],
      content: json['content'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class ChatSession {
  final String id;
  final String? recognitionText;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int messageCount;
  final List<ChatMessage> messages;

  ChatSession({
    required this.id,
    this.recognitionText,
    required this.createdAt,
    required this.updatedAt,
    required this.messageCount,
    required this.messages,
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      id: json['id'],
      recognitionText: json['recognition_text'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      messageCount: json['message_count'],
      messages: (json['messages'] as List)
          .map((m) => ChatMessage.fromJson(m))
          .toList(),
    );
  }
}

class AIQuota {
  final int dailyQuestionsUsed;
  final int totalQuestionsAsked;
  final DateTime lastResetDate;
  final bool canAsk;
  final int remainingQuestions; // -1 для unlimited
  final bool isPremium;

  AIQuota({
    required this.dailyQuestionsUsed,
    required this.totalQuestionsAsked,
    required this.lastResetDate,
    required this.canAsk,
    required this.remainingQuestions,
    required this.isPremium,
  });

  factory AIQuota.fromJson(Map<String, dynamic> json) {
    return AIQuota(
      dailyQuestionsUsed: json['daily_questions_used'],
      totalQuestionsAsked: json['total_questions_asked'],
      lastResetDate: DateTime.parse(json['last_reset_date']),
      canAsk: json['can_ask'],
      remainingQuestions: json['remaining_questions'],
      isPremium: json['is_premium'],
    );
  }
}
```

---

### 2. API Сервис

```dart
// lib/services/ai_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;

class AIService {
  static const String baseUrl = 'http://109.248.32.73/api/ai';
  
  // Отправить сообщение в чат
  static Future<Map<String, dynamic>> sendMessage({
    required String token,
    required String message,
    String? sessionId,
    String? recognitionText,
    String language = 'ru',
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/chat/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'message': message,
        if (sessionId != null) 'session_id': sessionId,
        if (recognitionText != null) 'recognition_text': recognitionText,
        'language': language,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } else if (response.statusCode == 403) {
      // Лимит исчерпан
      final error = jsonDecode(utf8.decode(response.bodyBytes));
      throw Exception(error['error']);
    } else {
      throw Exception('Ошибка отправки сообщения: ${response.statusCode}');
    }
  }

  // Быстрое действие
  static Future<Map<String, dynamic>> quickAction({
    required String token,
    required String action,
    required String text,
    String language = 'ru',
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/quick-action/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'action': action,
        'text': text,
        'language': language,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(utf8.decode(response.bodyBytes));
    } else if (response.statusCode == 403) {
      final error = jsonDecode(utf8.decode(response.bodyBytes));
      throw Exception(error['error']);
    } else {
      throw Exception('Ошибка выполнения действия: ${response.statusCode}');
    }
  }

  // Получить историю чатов
  static Future<List<ChatSession>> getChatHistory(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/history/'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(utf8.decode(response.bodyBytes));
      return data.map((json) => ChatSession.fromJson(json)).toList();
    } else {
      throw Exception('Ошибка загрузки истории: ${response.statusCode}');
    }
  }

  // Получить сессию чата
  static Future<ChatSession> getChatSession(String token, String sessionId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/session/$sessionId/'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return ChatSession.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    } else {
      throw Exception('Ошибка загрузки сессии: ${response.statusCode}');
    }
  }

  // Удалить сессию
  static Future<void> deleteChatSession(String token, String sessionId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/session/$sessionId/delete/'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode != 204) {
      throw Exception('Ошибка удаления сессии: ${response.statusCode}');
    }
  }

  // Получить квоту
  static Future<AIQuota> getQuota(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/quota/'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return AIQuota.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    } else {
      throw Exception('Ошибка загрузки квоты: ${response.statusCode}');
    }
  }
}
```

---

### 3. Пример UI - Экран чата

```dart
// lib/screens/ai_chat_screen.dart

import 'package:flutter/material.dart';

class AIChatScreen extends StatefulWidget {
  final String? recognitionText; // Текст из OCR
  final String? sessionId; // Для продолжения существующего чата

  const AIChatScreen({
    Key? key,
    this.recognitionText,
    this.sessionId,
  }) : super(key: key);

  @override
  State<AIChatScreen> createState() => _AIChatScreenState();
}

class _AIChatScreenState extends State<AIChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  String? _currentSessionId;
  bool _isLoading = false;
  int _remainingQuestions = 5;

  @override
  void initState() {
    super.initState();
    _currentSessionId = widget.sessionId;
    if (_currentSessionId != null) {
      _loadSession();
    }
    _loadQuota();
  }

  Future<void> _loadSession() async {
    // Загрузить существующую сессию
    try {
      final token = await _getToken(); // Ваш метод получения токена
      final session = await AIService.getChatSession(token, _currentSessionId!);
      setState(() {
        _messages.clear();
        _messages.addAll(session.messages);
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка загрузки чата: $e')),
      );
    }
  }

  Future<void> _loadQuota() async {
    try {
      final token = await _getToken();
      final quota = await AIService.getQuota(token);
      setState(() {
        _remainingQuestions = quota.remainingQuestions;
      });
    } catch (e) {
      print('Ошибка загрузки квоты: $e');
    }
  }

  Future<void> _sendMessage() async {
    if (_messageController.text.trim().isEmpty) return;

    final userMessage = _messageController.text.trim();
    _messageController.clear();

    // Добавляем сообщение пользователя в UI
    setState(() {
      _messages.add(ChatMessage(
        id: DateTime.now().toString(),
        role: 'user',
        content: userMessage,
        createdAt: DateTime.now(),
      ));
      _isLoading = true;
    });

    try {
      final token = await _getToken();
      final response = await AIService.sendMessage(
        token: token,
        message: userMessage,
        sessionId: _currentSessionId,
        recognitionText: widget.recognitionText,
        language: 'ru',
      );

      setState(() {
        _currentSessionId = response['session_id'];
        _remainingQuestions = response['remaining_questions'];
        _messages.add(ChatMessage(
          id: DateTime.now().toString(),
          role: 'assistant',
          content: response['response'],
          createdAt: DateTime.now(),
        ));
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка: $e')),
      );
    }
  }

  Future<String> _getToken() async {
    // Ваш метод получения JWT токена из SharedPreferences/Secure Storage
    return 'your_jwt_token';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Ассистент'),
        actions: [
          if (_remainingQuestions >= 0)
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Center(
                child: Text(
                  'Осталось: $_remainingQuestions',
                  style: const TextStyle(fontSize: 14),
                ),
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          // Контекст (распознанный текст)
          if (widget.recognitionText != null)
            Container(
              padding: const EdgeInsets.all(12),
              color: Colors.blue.shade50,
              child: Row(
                children: [
                  const Icon(Icons.info_outline, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Контекст: ${widget.recognitionText}',
                      style: const TextStyle(fontSize: 12),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ),

          // Список сообщений
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message.role == 'user';

                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(12),
                    constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.7,
                    ),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.blue : Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      message.content,
                      style: TextStyle(
                        color: isUser ? Colors.white : Colors.black87,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          // Индикатор загрузки
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: CircularProgressIndicator(),
            ),

          // Поле ввода
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: const InputDecoration(
                      hintText: 'Введите сообщение...',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: null,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  icon: const Icon(Icons.send),
                  color: Colors.blue,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

---

### 4. Пример - Быстрые действия

```dart
// lib/screens/quick_actions_screen.dart

class QuickActionsScreen extends StatelessWidget {
  final String recognitionText;

  const QuickActionsScreen({
    Key? key,
    required this.recognitionText,
  }) : super(key: key);

  Future<void> _performAction(BuildContext context, String action) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final token = await _getToken();
      final result = await AIService.quickAction(
        token: token,
        action: action,
        text: recognitionText,
        language: 'ru',
      );

      Navigator.pop(context); // Закрыть loading

      // Показать результат
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Результат'),
          content: Text(result['result']),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    } catch (e) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ошибка: $e')),
      );
    }
  }

  Future<String> _getToken() async {
    return 'your_jwt_token';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Быстрые действия')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Распознанный текст
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Распознанный текст:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(recognitionText),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Кнопки действий
          _ActionButton(
            icon: Icons.translate,
            label: 'Перевести на русский',
            onPressed: () => _performAction(context, 'translate_ru'),
          ),
          _ActionButton(
            icon: Icons.translate,
            label: 'Перевести на казахский',
            onPressed: () => _performAction(context, 'translate_kk'),
          ),
          _ActionButton(
            icon: Icons.translate,
            label: 'Перевести на английский',
            onPressed: () => _performAction(context, 'translate_en'),
          ),
          _ActionButton(
            icon: Icons.edit,
            label: 'Исправить ошибки',
            onPressed: () => _performAction(context, 'correct'),
          ),
          _ActionButton(
            icon: Icons.summarize,
            label: 'Краткое резюме',
            onPressed: () => _performAction(context, 'summarize'),
          ),
          _ActionButton(
            icon: Icons.help_outline,
            label: 'Объяснить текст',
            onPressed: () => _performAction(context, 'explain'),
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: Colors.blue),
        title: Text(label),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onPressed,
      ),
    );
  }
}
```

---

## 💰 Лимиты и монетизация

### Free пользователи
- **5 вопросов в день** (AI чат + быстрые действия)
- Счётчик сбрасывается в 00:00 UTC каждый день
- При достижении лимита показывать предложение обновиться до Premium

### Premium пользователи
- **Unlimited** вопросов
- `remaining_questions` = `-1` (означает unlimited)

### Проверка лимита
```dart
// Перед отправкой сообщения проверяйте квоту
final quota = await AIService.getQuota(token);

if (!quota.canAsk) {
  // Показать диалог с предложением Premium
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      title: const Text('Лимит исчерпан'),
      content: const Text(
        'Вы достигли дневного лимита (5 вопросов). '
        'Обновитесь до Premium для unlimited доступа к AI ассистенту.'
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Отмена'),
        ),
        ElevatedButton(
          onPressed: () {
            // Перейти на экран Premium подписки
          },
          child: const Text('Обновить до Premium'),
        ),
      ],
    ),
  );
  return;
}
```

---

## 🎨 Рекомендации по UX

### 1. **Интеграция с OCR экраном**
После успешного распознавания текста, показывать кнопки:
- "Задать вопрос AI" → открывает чат с контекстом
- "Быстрые действия" → показывает список действий

### 2. **История чатов**
Создайте отдельный экран "История AI чатов":
- Список всех сессий с preview первого сообщения
- Возможность продолжить чат
- Возможность удалить чат
- Поиск по истории

### 3. **Индикатор квоты**
Показывайте оставшиеся вопросы:
- В AppBar на экране чата
- На главном экране (badge)
- Анимация при приближении к лимиту

### 4. **Предложения Premium**
Когда пользователь достигает лимита:
- Показать красивый диалог с преимуществами Premium
- Добавить кнопку "Попробовать Premium" на экране квоты

### 5. **Быстрые действия**
Добавьте bottom sheet с быстрыми действиями прямо на экране результата OCR:
```dart
showModalBottomSheet(
  context: context,
  builder: (context) => QuickActionsSheet(text: recognizedText),
);
```

---

## ⚠️ Важные замечания

1. **API ключ OpenAI должен быть добавлен в админ-панели:**
   - Зайти на http://109.248.32.73/dashboard/settings/
   - Добавить ключ с типом "OpenAI (ChatGPT-4 Vision)"

2. **Обработка ошибок:**
   - 403 - лимит исчерпан (показать предложение Premium)
   - 500 - ошибка AI (показать "Попробуйте позже")
   - Нет интернета - показать соответствующее сообщение

3. **Оптимизация:**
   - Кэшируйте историю чатов локально
   - Используйте pagination для истории (если будет много чатов)
   - Показывайте индикатор загрузки при ожидании ответа сервера

4. **Безопасность:**
   - Всегда используйте JWT токен в заголовках
   - Не храните токен в открытом виде (используйте flutter_secure_storage)

---

## 📊 Swagger документация

Полная документация доступна по адресу:
**http://109.248.32.73/swagger/**

Там можно протестировать все эндпоинты прямо в браузере.

---

## ✅ Чеклист для Flutter разработчика

- [ ] Создать модели данных (ChatMessage, ChatSession, AIQuota)
- [ ] Реализовать AIService с методами для всех эндпоинтов
- [ ] Создать экран AI чата с историей сообщений
- [ ] Добавить экран быстрых действий
- [ ] Реализовать экран истории чатов
- [ ] Добавить проверку квоты перед отправкой сообщений
- [ ] Интегрировать с OCR экраном (кнопки "Задать вопрос", "Быстрые действия")
- [ ] Добавить индикатор оставшихся вопросов
- [ ] Реализовать диалог предложения Premium при достижении лимита
- [ ] Добавить обработку ошибок (403, 500, нет интернета)
- [ ] Протестировать все сценарии (новый чат, продолжение чата, быстрые действия)
- [ ] Добавить локальное кэширование истории чатов

---

## Итог

Выше перечислены эндпоинты, форматы JSON и ориентир по экранам Flutter. Проверка контракта — через Swagger на сервере (`/swagger/`).
