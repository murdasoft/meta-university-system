#!/bin/bash

# Загружаем исправленный файл на сервер
echo "Загружаем services.py на сервер..."

# Используем expect для автоматического ввода пароля
expect <<EOF
set timeout 30
spawn scp -P 22 ocr/services.py meta-university@109.248.32.73:/var/www/meta-university/ocr/
expect {
    "password:" {
        send "Dd06092000%\r"
        exp_continue
    }
    "Permission denied" {
        puts "❌ Неверный пароль!"
        exit 1
    }
    eof {
        puts "✅ Файл загружен!"
    }
}
EOF

echo ""
echo "Перезапускаем Gunicorn..."

expect <<EOF
set timeout 30
spawn ssh -p 22 meta-university@109.248.32.73 "sudo systemctl restart gunicorn"
expect {
    "password:" {
        send "Dd06092000%\r"
        exp_continue
    }
    eof
}
EOF

echo "✅ Готово!"
