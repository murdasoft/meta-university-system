#!/usr/bin/env python3
"""
Сервер: создаёт клиента интеграции в БД и файл /var/www/meta-university/.env.telegram
(токен и ключ не попадают в git).

Запуск от root на сервере:
  cd /var/www/meta-university
  export TELEGRAM_BOT_TOKEN='...'
  python deploy/setup_telegram_env.py
  chown meta-university:www-data .env.telegram
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'danadjango.settings')
os.chdir(BASE_DIR)

import django

django.setup()

from metapko.models import IntegrationClient  # noqa: E402


def main() -> None:
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print('Укажите TELEGRAM_BOT_TOKEN', file=sys.stderr)
        sys.exit(1)
    api_base = os.environ.get('METAPKO_API_BASE', 'http://109.248.32.73').rstrip('/')
    hdr = os.environ.get('METAPKO_API_KEY_HEADER', 'X-Meta-PKO-Key')

    env_path = BASE_DIR / '.env.telegram'
    if env_path.exists():
        print(f'Файл уже есть: {env_path} — удалите его перед повтором, если нужно пересоздать ключ.', file=sys.stderr)
        sys.exit(1)

    name = 'Telegram bot (server)'
    if IntegrationClient.objects.filter(name=name).exists():
        print(f'Клиент интеграции «{name}» уже есть в БД — удалите в meta-admin или переименуйте.', file=sys.stderr)
        sys.exit(1)

    c = IntegrationClient(name=name)
    raw = IntegrationClient.generate_raw_key()
    c.set_key(raw)
    c.save()

    env_path.write_text(
        f'TELEGRAM_BOT_TOKEN={token}\n'
        f'METAPKO_API_BASE={api_base}\n'
        f'METAPKO_API_KEY={raw}\n'
        f'METAPKO_API_KEY_HEADER={hdr}\n',
        encoding='utf-8',
    )
    env_path.chmod(0o600)
    try:
        import grp
        import pwd

        uid = pwd.getpwnam('meta-university').pw_uid
        gid = grp.getgrnam('www-data').gr_gid
        os.chown(env_path, uid, gid)
    except (KeyError, OSError):
        pass

    print(f'OK: {env_path}, integration client id={c.pk}')


if __name__ == '__main__':
    main()
