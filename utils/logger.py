import logging
import os
from logging.handlers import RotatingFileHandler
import sys

def setup_logger():
    """Настройка логирования"""
    # Создаем директорию для логов, если её нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Настройка логгера
    logger = logging.getLogger('sapphire_bot')
    logger.setLevel(logging.INFO)
    
    # Форматирование логов
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Обработчик для вывода в файл с ротацией (максимум 5 файлов по 5 МБ)
    file_handler = RotatingFileHandler(
        'logs/sapphire_bot.log',
        maxBytes=5 * 1024 * 1024,  # 5 МБ
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    
    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger