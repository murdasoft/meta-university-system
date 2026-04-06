#!/usr/bin/env python3
"""
Простой Telegram-бот для API /api/metapko/v1/.

Установка:
  pip install python-telegram-bot httpx

Переменные окружения:
  TELEGRAM_BOT_TOKEN       — от @BotFather
  METAPKO_API_BASE         — https://ваш-домен  или http://109.248.32.73 (без слэша в конце)
  METAPKO_API_KEY          — ключ из meta-admin → Клиенты интеграции
  METAPKO_API_KEY_HEADER   — по умолчанию X-Meta-PKO-Key

Запуск:
  export TELEGRAM_BOT_TOKEN='...'
  export METAPKO_API_BASE='http://109.248.32.73'
  export METAPKO_API_KEY='...'
  python scripts/telegram_metapko_bot.py

Команды см. /start и документацию документация/09_TELEGRAM_IIKO_METAPKO.md
"""

from __future__ import annotations

import logging
import os
import sys

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _env(name: str, default: str | None = None) -> str:
    v = os.environ.get(name, default)
    if not v:
        print(f"Задайте переменную окружения {name}", file=sys.stderr)
        sys.exit(1)
    return v


BASE = _env("METAPKO_API_BASE").rstrip("/")
KEY = _env("METAPKO_API_KEY")
HDR = os.environ.get("METAPKO_API_KEY_HEADER", "X-Meta-PKO-Key")
TOKEN = _env("TELEGRAM_BOT_TOKEN")


def _headers() -> dict:
    return {HDR: KEY}


def _results(data):
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    if isinstance(data, list):
        return data
    return []


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Команды Meta-университет / metapko API:\n\n"
        "/ping — health + /me\n"
        "/programs — учебные программы\n"
        "/groups — учебные группы\n"
        "/rooms — аудитории (справочник)\n"
        "/teachers — преподаватели\n"
        "/sessions — ближайшие занятия\n"
        "/calendar — события календаря\n"
        "/news — новости и объявления\n"
        "/contacts — справочник контактов\n"
        "/faq — FAQ\n\n"
        "Данные из /api/metapko/v1/ с вашим API-ключом."
    )


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{BASE}/api/metapko/v1/health/")
        m = await client.get(f"{BASE}/api/metapko/v1/me/", headers=_headers())
    await update.message.reply_text(
        f"health: {r.status_code}\n{r.text[:400]}\n\n"
        f"me: {m.status_code}\n{m.text[:400]}"
    )


async def cmd_programs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{BASE}/api/metapko/v1/study-programs/",
            headers=_headers(),
            params={"ordering": "sort_order"},
        )
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Список программ пуст.")
        return
    lines = []
    for row in rows[:20]:
        code = row.get("code") or ""
        lvl = row.get("level") or ""
        name = row.get("name", "?")
        lines.append(f"• {name}" + (f" ({code})" if code else "") + (f" — {lvl}" if lvl else ""))
    await update.message.reply_text("\n".join(lines))


async def cmd_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{BASE}/api/metapko/v1/study-groups/",
            headers=_headers(),
            params={"ordering": "sort_order"},
        )
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Групп нет в базе.")
        return
    lines = []
    for row in rows[:20]:
        name = row.get("name", "?")
        pn = row.get("program_name") or ""
        iy = row.get("intake_year")
        suf = f" — {pn}" if pn else ""
        if iy:
            suf += f", {iy} г."
        lines.append(f"• {name}{suf}")
    await update.message.reply_text("\n".join(lines))


async def cmd_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{BASE}/api/metapko/v1/rooms/", headers=_headers())
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Аудиторий в справочнике нет.")
        return
    lines = []
    for row in rows[:25]:
        nm = row.get("name", "?")
        bc = row.get("building_code") or row.get("building_name") or ""
        lines.append(f"• {bc + ', ' if bc else ''}{nm}".strip())
    await update.message.reply_text("\n".join(lines))


async def cmd_teachers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{BASE}/api/metapko/v1/teachers/", headers=_headers())
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Список пуст. Добавьте преподавателей в meta-admin.")
        return
    lines = []
    for t in rows[:15]:
        name = t.get("full_name", "?")
        dep = t.get("department_name") or ""
        lines.append(f"• {name}" + (f" ({dep})" if dep else ""))
    await update.message.reply_text("\n".join(lines))


async def cmd_sessions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{BASE}/api/metapko/v1/class-sessions/",
            headers=_headers(),
            params={"ordering": "starts_at"},
        )
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Занятий нет в базе.")
        return
    lines = []
    for s in rows[:10]:
        ct = s.get("course_title") or ""
        loc = (s.get("room_display") or s.get("room") or "").strip()
        start = s.get("starts_at") or ""
        lines.append(f"• {start[:16]} — {ct}" + (f" ({loc})" if loc else ""))
    await update.message.reply_text("\n".join(lines))


async def cmd_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{BASE}/api/metapko/v1/calendar/",
            headers=_headers(),
            params={"ordering": "starts_on"},
        )
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Событий календаря нет.")
        return
    lines = []
    for row in rows[:12]:
        title = row.get("title", "?")
        k = row.get("kind_display") or row.get("kind") or ""
        d0 = str(row.get("starts_on") or "")
        d1 = row.get("ends_on")
        if d1:
            lines.append(f"• {d0}—{d1}: {title} ({k})")
        else:
            lines.append(f"• {d0}: {title} ({k})")
    await update.message.reply_text("\n".join(lines))


async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{BASE}/api/metapko/v1/news/",
            headers=_headers(),
        )
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Новостей нет.")
        return
    parts = []
    for row in rows[:6]:
        title = row.get("title", "")
        summ = (row.get("summary") or "")[:220]
        pin = "📌 " if row.get("is_pinned") else ""
        parts.append(f"{pin}{title}\n{summ}")
    await update.message.reply_text("\n\n".join(parts))


async def cmd_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(
            f"{BASE}/api/metapko/v1/contacts/",
            headers=_headers(),
            params={"ordering": "sort_order"},
        )
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("Контактов нет.")
        return
    parts = []
    for row in rows[:12]:
        title = row.get("title", "?")
        role = row.get("role_hint") or ""
        phone = row.get("phone") or ""
        email = row.get("email") or ""
        addr = row.get("address") or ""
        hours = row.get("office_hours") or ""
        block = [title]
        if role:
            block.append(f"({role})")
        if phone:
            block.append(f"тел.: {phone}")
        if email:
            block.append(email)
        if addr:
            block.append(addr)
        if hours:
            block.append(f"часы: {hours}")
        parts.append("\n".join(block))
    await update.message.reply_text("\n\n—\n\n".join(parts))


async def cmd_faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{BASE}/api/metapko/v1/faq/", headers=_headers())
    if r.status_code != 200:
        await update.message.reply_text(f"Ошибка {r.status_code}: {r.text[:500]}")
        return
    rows = _results(r.json())
    if not rows:
        await update.message.reply_text("FAQ пуст.")
        return
    parts = []
    for row in rows[:5]:
        q = row.get("question", "")
        a = (row.get("answer") or "")[:300]
        parts.append(f"Q: {q}\nA: {a}")
    await update.message.reply_text("\n\n".join(parts))


def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ping", cmd_ping))
    app.add_handler(CommandHandler("programs", cmd_programs))
    app.add_handler(CommandHandler("groups", cmd_groups))
    app.add_handler(CommandHandler("rooms", cmd_rooms))
    app.add_handler(CommandHandler("teachers", cmd_teachers))
    app.add_handler(CommandHandler("sessions", cmd_sessions))
    app.add_handler(CommandHandler("calendar", cmd_calendar))
    app.add_handler(CommandHandler("news", cmd_news))
    app.add_handler(CommandHandler("contacts", cmd_contacts))
    app.add_handler(CommandHandler("faq", cmd_faq))
    logger.info("Бот запущен (polling). Останов: Ctrl+C")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
