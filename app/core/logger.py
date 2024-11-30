# app/core/logger.py

import logging
import logging.handlers
import os
from app.core.config import Config

# Загружаем конфигурации
config = Config()

# Настройки логирования
log_level = config.logging.level
log_file = config.paths.logs
log_format = config.logging.format
max_bytes = config.logging.max_bytes
backup_count = config.logging.backup_count

# Убеждаемся, что директория для логов существует
log_dir = os.path.dirname(log_file)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Создаем обработчики
stream_handler = logging.StreamHandler()
file_handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
)

# Настраиваем форматтер
formatter = logging.Formatter(log_format)
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Настраиваем логгер
logger = logging.getLogger()
logger.setLevel(log_level)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
