# 🚀 Быстрый деплой Qazaq Dana

## 🎯 Самый быстрый способ (3 команды)

```bash
# 1. Перейдите в папку проекта
cd /Users/daniyarmukhtarov/Desktop/project/qazaqdana/danadjango

# 2. Сделайте скрипты исполняемыми
chmod +x deploy/*.sh

# 3. Запустите деплой
./deploy/simple_deploy.sh
```

Скрипт автоматически:
- ✅ Подключится к серверу
- ✅ Установит все необходимые пакеты
- ✅ Настроит PostgreSQL
- ✅ Создаст структуру директорий

После этого вам нужно будет загрузить файлы проекта (команда будет показана в конце).

---

## 📋 Альтернативный способ (вручную, по шагам)

### Шаг 1: Подключение к серверу

```bash
ssh root@109.248.32.73
# Пароль: zt7RM#q3;o70ZM
```

### Шаг 2: Загрузка deployment скриптов

На сервере выполните:

```bash
# Создайте временную директорию
mkdir -p /root/qazaqdana-deploy
cd /root/qazaqdana-deploy

# Скачайте скрипты (вариант 1 - через git, если проект в репозитории)
git clone <URL-вашего-репозитория> .

# ИЛИ вариант 2 - загрузите файлы с локального компьютера
# На ЛОКАЛЬНОМ компьютере выполните:
# scp -r deploy/ root@109.248.32.73:/root/qazaqdana-deploy/
```

### Шаг 3: Запуск деплоя (на сервере)

```bash
cd /root/qazaqdana-deploy
chmod +x deploy/*.sh

# Запустите скрипты по порядку
bash deploy/deploy_step1.sh
```

### Шаг 4: Загрузка файлов проекта

На ЛОКАЛЬНОМ компьютере:

```bash
cd /Users/daniyarmukhtarov/Desktop/project/qazaqdana/danadjango

# Загрузка файлов через rsync
rsync -avz --progress \
    --exclude='venv*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='db.sqlite3' \
    --exclude='media/*' \
    root@109.248.32.73:/var/www/qazaqdana/
```

### Шаг 5: Завершение установки (на сервере)

```bash
ssh root@109.248.32.73
cd /var/www/qazaqdana

# Продолжение деплоя
bash deploy/deploy_step2.sh
bash deploy/deploy_step3.sh
```

---

## ✅ После деплоя

### Проверка работы

Откройте в браузере: **http://109.248.32.73**

### Вход в систему

- **URL**: http://109.248.32.73/login/
- **Логин**: admin
- **Пароль**: admin123

### Полезные команды

```bash
# Статус приложения
ssh root@109.248.32.73 'systemctl status qazaqdana'

# Просмотр логов
ssh root@109.248.32.73 'journalctl -u qazaqdana -f'

# Перезапуск приложения
ssh root@109.248.32.73 'systemctl restart qazaqdana'

# Перезапуск Nginx
ssh root@109.248.32.73 'systemctl restart nginx'
```

---

## 🔄 Обновление приложения

Когда нужно обновить код на сервере:

```bash
# 1. На локальном компьютере
cd /Users/daniyarmukhtarov/Desktop/project/qazaqdana/danadjango
rsync -avz --exclude='venv*' --exclude='__pycache__' --exclude='.git' ./ root@109.248.32.73:/var/www/qazaqdana/

# 2. На сервере применить изменения
ssh root@109.248.32.73 << 'EOF'
cd /var/www/qazaqdana
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart qazaqdana
EOF
```

---

## 🆘 Решение проблем

### Приложение не открывается

```bash
# Проверьте статус
ssh root@109.248.32.73 'systemctl status qazaqdana nginx'

# Посмотрите логи
ssh root@109.248.32.73 'tail -f /var/www/qazaqdana/logs/gunicorn-error.log'
```

### Ошибка 502 Bad Gateway

```bash
# Перезапустите сервисы
ssh root@109.248.32.73 'systemctl restart qazaqdana nginx'
```

### Статика не загружается

```bash
ssh root@109.248.32.73 << 'EOF'
cd /var/www/qazaqdana
source venv/bin/activate
python manage.py collectstatic --noinput --clear
systemctl restart nginx
EOF
```

---

## 📝 Важные файлы

| Файл | Описание |
|------|----------|
| `deploy_step1.sh` | Установка системных пакетов и PostgreSQL |
| `deploy_step2.sh` | Установка Python зависимостей и миграции |
| `deploy_step3.sh` | Настройка Gunicorn, Nginx, запуск сервисов |
| `DEPLOYMENT_GUIDE.md` | Подробная документация |
| `.env.production` | Шаблон production конфигурации |

---

## 🎉 Готово!

После успешного деплоя ваше приложение будет доступно по адресу:

**http://109.248.32.73**

Не забудьте:
- ✅ Сменить пароль администратора
- ✅ Обновить SECRET_KEY в .env
- ✅ Настроить домен (опционально)
- ✅ Установить SSL сертификат (опционально)
