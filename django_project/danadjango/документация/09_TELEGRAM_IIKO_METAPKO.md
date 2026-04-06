# Telegram-бот и API IIKO / Meta-университет

Это моя внутренняя памятка: что я уже сделал в проекте, что у меня есть «из коробки» и как я обычно с этим работаю.

---

## Что я сделал и что у меня есть

Я подключил **Telegram-бота** к своему backend **Meta-университет / metapko**: бот ходит по HTTP(S) на тот же хост, где крутится Django, и дергает REST **`/api/metapko/v1/`** с API-ключом в заголовке.

**У меня в репозитории уже лежит:**

- Готовый скрипт **`scripts/telegram_metapko_bot.py`** (python-telegram-bot v20 + httpx). В нём команды для программ, групп, аудиторий, преподавателей, занятий, календаря, новостей, контактов, FAQ и проверка `/ping`.
- Список строк для меню BotFather: **`deploy/botfather_metapko_commands.txt`** — я вставляю его в [@BotFather](https://t.me/BotFather) через **`/setcommands`**, чтобы у бота появилась кнопка «Menu» с подсказками.
- На сервере я могу держать бота как **systemd**-сервис (например `telegram-metapko-bot`) с переменными в **`.env.telegram`** или в `Environment=` unit-файла — токен и ключ в git я не коммичу.

**На стороне API у меня:**

- Клиенты интеграции и ключи — только в **meta-admin** (`/meta-admin/`), раздел «Клиенты интеграции»; в БД хранится хеш, сырой ключ я вижу один раз при создании.
- Заголовок ключа по умолчанию я использую **`X-Meta-PKO-Key`** (если переопределил — смотрю `METAPKO_API_KEY_HEADER` в `.env`).
- Данные для бота я наполняю через **портал** `/metapko/dashboard/` или **meta-admin**; при необходимости прогоняю **`python manage.py seed_metapko_bulk --clear`** на сервере.

---

## Как я работаю: быстрый чеклист

1. Я получаю **токен** у [@BotFather](https://t.me/BotFather) (`/newbot`) и сохраняю его отдельно от кода.
2. Захожу в **meta-admin** под **staff**, создаю **клиента интеграции**, копирую **API-ключ** (показывается один раз).
3. На машине, где крутится бот, ставлю зависимости: **`pip install python-telegram-bot httpx`** (Python 3.10+).
4. Выставляю переменные окружения (см. ниже) и запускаю **`python scripts/telegram_metapko_bot.py`** либо перезапускаю systemd-сервис бота.
5. В Telegram пишу своему боту **`/start`**, затем **`/ping`** и остальные команды по необходимости.

---

## Как я получаю ключ API на сервере

1. Открываю **`http://мой-сервер/meta-admin/`** (только учётка с флагом staff).
2. **«Клиенты интеграции»** → **Добавить**, ввожу название (например `Telegram bot`) → **Сохранить**.
3. Копирую **сырой ключ** в безопасное место — повторно его не покажут, в базе останется только хеш.

---

## Как я настраиваю окружение бота

```bash
pip install python-telegram-bot httpx
```

**Переменные, которые я задаю** (в оболочке или в unit-файле, не в git):

| Переменная | Для чего |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | токен от BotFather |
| `METAPKO_API_BASE` | база без слэша в конце, напр. `http://109.248.32.73` или `https://мой-домен` |
| `METAPKO_API_KEY` | сырой ключ из meta-admin |
| `METAPKO_API_KEY_HEADER` | опционально, если на сервере не дефолтный заголовок |

**Локальный запуск** (macOS/Linux), из каталога проекта:

```bash
cd /путь/к/danadjango
python3 -m venv .venv-telegram
source .venv-telegram/bin/activate
pip install python-telegram-bot httpx

export TELEGRAM_BOT_TOKEN='МОЙ_ТОКЕН'
export METAPKO_API_BASE='http://109.248.32.73'
export METAPKO_API_KEY='МОЙ_КЛЮЧ'
# при необходимости:
# export METAPKO_API_KEY_HEADER='X-Meta-PKO-Key'

python scripts/telegram_metapko_bot.py
```

Терминал держу открытым, пока нужен **polling**; останов — `Ctrl+C`.

**Windows (cmd):**

```bat
set TELEGRAM_BOT_TOKEN=мой_токен
set METAPKO_API_BASE=http://109.248.32.73
set METAPKO_API_KEY=мой_ключ
python scripts\telegram_metapko_bot.py
```

---

## Минимальный пример кода (если я хочу свой маленький скрипт)

Иногда я проверяю только health и `/me`:

```python
import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BASE = os.environ["METAPKO_API_BASE"].rstrip("/")
KEY = os.environ["METAPKO_API_KEY"]
HDR = os.environ.get("METAPKO_API_KEY_HEADER", "X-Meta-PKO-Key")

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(f"{BASE}/api/metapko/v1/health/")
        h = await client.get(
            f"{BASE}/api/metapko/v1/me/",
            headers={HDR: KEY},
        )
    await update.message.reply_text(
        f"health: {r.status_code} {r.text[:200]}\nme: {h.status_code} {h.text[:300]}"
    )

def main():
    app = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.run_polling()

if __name__ == "__main__":
    main()
```

Полную логику я всё равно держу в **`scripts/telegram_metapko_bot.py`**.

---

## Webhook вместо polling

Если я захочу **webhook** на проде: нужен **HTTPS**, у BotFather — `/setwebhook` на URL вида `https://мой-домен/telegram/webhook/`, в Django — отдельный view и проверка секрета `X-Telegram-Bot-Api-Secret-Token`. Сейчас я чаще пользуюсь **polling** через systemd — так проще на этапе, когда домен с Let's Encrypt ещё не обязателен.

---

## Безопасность — что я для себя фиксирую

- Токен бота и API-ключ **не кладу** в репозиторий.
- В проде по возможности включаю **HTTPS** к API.
- После тестов **меняю** пароли и при необходимости отключаю подсказки на форме входа в портал (`METAPKO_PORTAL_HINT_*` в `.env`).

---

## Мои полезные URL

| Назначение | Путь |
|------------|------|
| Портал быстрого ввода | `/metapko/dashboard/` |
| Админка metapko | `/meta-admin/` |
| Swagger | `/meta-swagger/` |
| Проверка без ключа | `GET /api/metapko/v1/health/` |
| Проверка с ключом | `GET /api/metapko/v1/me/` |

---

## Команды моего бота и что дергается в API

Я передаю в запросах заголовок с ключом (`X-Meta-PKO-Key` или мой `METAPKO_API_KEY_HEADER`). Все пути ниже — с префиксом `/api/metapko/v1/`.

| Команда в Telegram | Что я запрашиваю |
|--------------------|------------------|
| `/ping` | `health/` и `me/` |
| `/programs` | `study-programs/` |
| `/groups` | `study-groups/` |
| `/rooms` | `rooms/` |
| `/teachers` | `teachers/` |
| `/sessions` | `class-sessions/?ordering=starts_at` |
| `/calendar` | `calendar/?ordering=starts_on` |
| `/news` | `news/` |
| `/contacts` | `contacts/?ordering=sort_order` |
| `/faq` | `faq/` |

### Как я добавляю новую команду

1. Убеждаюсь, что в `metapko/api_urls.py` уже есть нужный эндпоинт.
2. В **`scripts/telegram_metapko_bot.py`** добавляю async-функцию по аналогии с `cmd_contacts` (httpx + `_headers()` + разбор `results`).
3. В **`main()`** регистрирую `CommandHandler("имя", функция)` без слэша в имени.
4. Обновляю текст **`cmd_start`** и при необходимости **`deploy/botfather_metapko_commands.txt`**, потом снова **`/setcommands`** в BotFather.
5. Перезапускаю процесс бота на сервере.

### Меню в BotFather

Я открываю [@BotFather](https://t.me/BotFather) → **`/setcommands`** → выбираю бота → вставляю строки из **`deploy/botfather_metapko_commands.txt`** (формат: `команда - описание`, **без** `/` у команды). Это только подсказка в интерфейсе Telegram; реальная логика — в скрипте.

---

**Итог:** я связал бота с тем же Django **metapko**, что и портал с быстрыми формами; данные я правлю в админке или на дашборде, а бот только читает их через API с моим ключом интеграции.
