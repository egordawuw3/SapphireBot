import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройки бота
BOT_PREFIX = "!"
BOT_DESCRIPTION = "Многофункциональный Discord-бот для сервера Sapphire Creators"

# Настройки базы данных
DATABASE_PATH = "data/sapphire.db"

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "logs/sapphire_bot.log"
LOG_MAX_SIZE = 5 * 1024 * 1024  # 5 МБ
LOG_BACKUP_COUNT = 5

# Настройки API ключей
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Настройки для yt-dlp
YDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}