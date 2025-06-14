# SapphireBot 🤖

✨ Многофункциональный Discord бот для сообщества Sapphire Creators

## Основные функции
- 🎮 Система уровней
- 🎵 Музыкальный плеер
- 🤖 AI чат
- 🛠️ Утилиты

## Использование с MySQL

1. Установите MySQL сервер (или MariaDB).
2. Создайте базу данных и пользователя без пароля:

```sql
CREATE DATABASE sapphirebot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'botuser'@'%' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON sapphirebot.* TO 'botuser'@'%';
FLUSH PRIVILEGES;
```

3. Таблицы создаются автоматически при первом запуске бота.

4. В .env или config/constants.py (или прямо в Database) укажите параметры подключения:
   - host: адрес MySQL сервера (например, 127.0.0.1)
   - user: botuser
   - password: (пусто)
   - database: sapphirebot

5. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

6. Запустите бота как обычно.

## Установка
1. Установите зависимости:
```bash
pip install -r requirements.txt
```