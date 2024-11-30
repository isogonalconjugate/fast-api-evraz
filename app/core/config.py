# app/core/config.py

import toml
from pathlib import Path


class LLMConfig:
    def __init__(self, config):
        self.model_name = config.get('model_name', 'ollama')


class PathsConfig:
    def __init__(self, config):
        self.unzip_dir = config.get('unzip_dir', 'temp_unzipped')
        self.prompts = config.get('prompts', 'app/llm_prompts/prompts.json')
        self.errors_list = config.get('errors_list', 'app/llm_prompts/errors_list.json')
        self.rules = config.get('rules', 'app/llm_prompts/rules.json')
        self.logs = config.get('logs', 'logs/app.log')
        self.project_root = config.get('project_root', None)


class LoggingConfig:
    def __init__(self, config):
        self.level = config.get('level', 'INFO').upper()
        self.file = config.get('file', 'logs/app.log')
        self.format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.max_bytes = config.get('max_bytes', 10485760)  # 10 MB
        self.backup_count = config.get('backup_count', 5)


import toml
from pathlib import Path

class Config:
    def __init__(self, config_file='config.toml'):
        # Get the directory where this config.py resides
        base_dir = Path(__file__).resolve().parent.parent.parent  # Adjust as needed
        self.config_file = base_dir / config_file
        if not self.config_file.exists():
            raise FileNotFoundError(f"Конфигурационный файл {self.config_file} не найден.")
        self.config = toml.load(self.config_file)

        # Initialize nested configurations
        self.llm = LLMConfig(self.config.get('llm', {}))
        self.paths = PathsConfig(self.config.get('paths', {}))
        self.logging = LoggingConfig(self.config.get('logging', {}))

    def get(self, section, key, default=None):
        """Получение значения из конфигурации по секции и ключу."""
        return self.config.get(section, {}).get(key, default)

    def set_project_root(self, path):
        """Устанавливает корневой каталог проекта."""
        self.paths.project_root = path
