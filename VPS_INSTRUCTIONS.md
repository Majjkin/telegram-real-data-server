# 🚀 Инструкция по настройке VPS

## Подключение к VPS

1. **Откройте терминал на вашем компьютере**

2. **Подключитесь к VPS:**
   ```bash
   ssh root@31.58.87.15
   ```

3. **Если первый раз, введите `yes` когда спросит про ключ**

4. **Введите пароль от VPS (из панели HostVDS)**

## Автоматическая настройка

1. **Скопируйте и выполните команду:**
   ```bash
   curl -s https://raw.githubusercontent.com/Majjkin/telegram-real-data-server/main/vps_setup.sh | bash
   ```

   **ИЛИ вручную:**

2. **Создайте файл настройки:**
   ```bash
   nano vps_setup.sh
   ```

3. **Скопируйте содержимое файла `vps_setup.sh` из локальной папки и вставьте**

4. **Сделайте исполняемым и запустите:**
   ```bash
   chmod +x vps_setup.sh
   ./vps_setup.sh
   ```

## Создание Telegram сессии

1. **Перейдите в папку проекта:**
   ```bash
   cd /opt/creative-mvp
   ```

2. **Запустите создание сессии:**
   ```bash
   python3 create_session.py
   ```

3. **Введите номер телефона (например: +1234567890)**

4. **Введите код из Telegram**

5. **Скопируйте полученную сессию**

6. **Обновите .env файл:**
   ```bash
   nano .env
   ```

7. **Замените `your_session_string_here` на полученную сессию**

## Запуск сервера

1. **Запустите сервер:**
   ```bash
   python3 vps_server.py
   ```

2. **Откройте в браузере:**
   **http://31.58.87.15:8000/ui**

## Автозапуск (опционально)

1. **Включите автозапуск:**
   ```bash
   systemctl daemon-reload
   systemctl enable creative-mvp
   systemctl start creative-mvp
   ```

2. **Проверьте статус:**
   ```bash
   systemctl status creative-mvp
   ```

## Проверка работы

- **API:** http://31.58.87.15:8000/
- **UI:** http://31.58.87.15:8000/ui
- **Логи:** `journalctl -u creative-mvp -f`

## Остановка сервера

```bash
systemctl stop creative-mvp
```

## Перезапуск сервера

```bash
systemctl restart creative-mvp
```
