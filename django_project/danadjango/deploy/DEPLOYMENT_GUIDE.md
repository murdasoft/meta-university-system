# Полный гайд по деплою Qazaq Dana на продакшен

## 🖥️ Информация о сервере

- **IP**: 109.248.32.73
- **OS**: Ubuntu 24.04
- **CPU**: 1 vCPU
- **RAM**: 3 GB
- **Storage**: 20 GB NVMe
- **SSH**: root@109.248.32.73

## 📋 Быстрый деплой (автоматический)

### Вариант 1: С локального компьютера (rsync)

```bash
# 1. Загрузка файлов на сервер
cd /Users/daniyarmukhtarov/Desktop/project/meta-university/danadjango
chmod +x deploy/*.sh
./deploy/upload_to_server.sh

# 2. Подключение к серверу
ssh root@109.248.32.73

# 3. Запуск деплоя (на сервере)
cd /var/www/meta-university
chmod +x deploy/*.sh
bash deploy/deploy_step1.sh
bash deploy/deploy_step2.sh
bash deploy/deploy_step3.sh
```

### Вариант 2: Прямо на сервере (через Git)

```bash
# 1. Подключение к серверу
ssh root@109.248.32.73

# 2. Клонирование проекта
apt-get update
apt-get install -y git
cd /root
git clone <your-repo-url> meta-university-temp
cd meta-university-temp

# 3. Запуск деплоя
chmod +x deploy/*.sh
bash deploy/deploy_step1.sh

# 4. Копирование файлов проекта
cp -r . /var/www/meta-university/
cd /var/www/meta-university

# 5. Продолжение деплоя
bash deploy/deploy_step2.sh
bash deploy/deploy_step3.sh
```

## 🔧 Ручной деплой (пошагово)

### Шаг 1: Подключение к серверу

```bash
ssh root@109.248.32.73
# Пароль: zt7RM#q3;o70ZM
```

### Шаг 2: Обновление системы

```bash
apt-get update
apt-get upgrade -y
```

### Шаг 3: Установка зависимостей

```bash
apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    supervisor \
    ufw
```

### Шаг 4: Настройка PostgreSQL

```bash
# Переключение на пользователя postgres
sudo -u postgres psql

# В psql выполните:
CREATE DATABASE meta-university_db;
CREATE USER meta-university_user WITH PASSWORD 'QazaqDana2026!SecurePass';
ALTER ROLE meta-university_user SET client_encoding TO 'utf8';
ALTER ROLE meta-university_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE meta-university_user SET timezone TO 'Asia/Almaty';
GRANT ALL PRIVILEGES ON DATABASE meta-university_db TO meta-university_user;
\q
```

### Шаг 5: Создание пользователя приложения

```bash
useradd -m -s /bin/bash meta-university
```

### Шаг 6: Загрузка проекта

```bash
# Создание директории
mkdir -p /var/www/meta-university
cd /var/www/meta-university

# Загрузка файлов (используйте один из методов):
# - Git clone (если проект в репозитории)
# - SCP с локального компьютера
# - rsync (рекомендуется)
```

### Шаг 7: Настройка Python окружения

```bash
cd /var/www/meta-university
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Шаг 8: Создание .env файла

```bash
nano .env
```

Содержимое:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=109.248.32.73

DB_NAME=meta-university_db
DB_USER=meta-university_user
DB_PASSWORD=QazaqDana2026!SecurePass
DB_HOST=localhost
DB_PORT=5432
```

### Шаг 9: Применение миграций и сбор статики

```bash
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # или init_data
deactivate
```

### Шаг 10: Настройка Gunicorn (systemd)

```bash
nano /etc/systemd/system/meta-university.service
```

Содержимое (скопируйте из deploy_step3.sh)

### Шаг 11: Настройка Nginx

```bash
nano /etc/nginx/sites-available/meta-university
```

Содержимое (скопируйте из deploy_step3.sh)

```bash
ln -s /etc/nginx/sites-available/meta-university /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
```

### Шаг 12: Настройка Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Шаг 13: Установка прав

```bash
chown -R meta-university:www-data /var/www/meta-university
chmod -R 755 /var/www/meta-university
mkdir -p /var/www/meta-university/logs
chmod -R 775 /var/www/meta-university/logs
```

### Шаг 14: Запуск сервисов

```bash
systemctl daemon-reload
systemctl enable meta-university
systemctl start meta-university
systemctl restart nginx
```

## ✅ Проверка работы

### Проверка статуса сервисов

```bash
systemctl status meta-university
systemctl status nginx
systemctl status postgresql
```

### Проверка логов

```bash
# Логи приложения
journalctl -u meta-university -f

# Логи Gunicorn
tail -f /var/www/meta-university/logs/gunicorn-error.log

# Логи Nginx
tail -f /var/log/nginx/error.log
tail -f /var/www/meta-university/logs/nginx-error.log
```

### Тест в браузере

Откройте: http://109.248.32.73

- Главная: http://109.248.32.73/
- Логин: http://109.248.32.73/login/
- Admin: admin / admin123

## 🔧 Управление сервисом

```bash
# Перезапуск приложения
systemctl restart meta-university

# Остановка
systemctl stop meta-university

# Старт
systemctl start meta-university

# Статус
systemctl status meta-university

# Логи в реальном времени
journalctl -u meta-university -f
```

## 🔄 Обновление приложения

```bash
# 1. На локальном компьютере загрузите новые файлы
./deploy/upload_to_server.sh

# 2. На сервере
ssh root@109.248.32.73
cd /var/www/meta-university
source venv/bin/activate

# 3. Применить миграции (если есть)
python manage.py migrate

# 4. Обновить статику
python manage.py collectstatic --noinput

# 5. Перезапустить сервис
systemctl restart meta-university
```

## 🔒 Настройка SSL (Let's Encrypt) - опционально

```bash
# Установка Certbot
apt-get install -y certbot python3-certbot-nginx

# Получение сертификата (после настройки домена)
certbot --nginx -d meta-university.kz -d www.meta-university.kz

# Автообновление сертификата
certbot renew --dry-run
```

## 📊 Мониторинг

```bash
# Использование диска
df -h

# Использование RAM
free -h

# Процессы
ps aux | grep gunicorn
ps aux | grep nginx

# Сетевые подключения
netstat -tulpn | grep :80
```

## 🆘 Решение проблем

### Приложение не запускается

```bash
# Проверьте логи
journalctl -u meta-university -n 50
tail -f /var/www/meta-university/logs/gunicorn-error.log

# Проверьте конфигурацию
nginx -t
systemctl status meta-university
```

### Ошибка подключения к БД

```bash
# Проверьте PostgreSQL
systemctl status postgresql
sudo -u postgres psql -c "\l"  # Список БД
sudo -u postgres psql -c "\du" # Список пользователей
```

### 502 Bad Gateway

```bash
# Проверьте gunicorn sock
ls -la /var/www/meta-university/gunicorn.sock

# Проверьте права
chown -R meta-university:www-data /var/www/meta-university
```

### Статика не загружается

```bash
# Пересоберите статику
cd /var/www/meta-university
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# Проверьте права
chmod -R 755 /var/www/meta-university/static
```

## 📝 Полезные команды

```bash
# Создание бэкапа БД
sudo -u postgres pg_dump meta-university_db > backup_$(date +%Y%m%d).sql

# Восстановление БД
sudo -u postgres psql meta-university_db < backup_20260211.sql

# Просмотр активных соединений
ss -tulpn

# Очистка логов
truncate -s 0 /var/www/meta-university/logs/*.log
```

## 🎉 Готово!

После успешного деплоя приложение будет доступно:
- **URL**: http://109.248.32.73
- **Логин**: admin
- **Пароль**: admin123

---

**Важно**: Не забудьте сменить пароли и SECRET_KEY в продакшене!
