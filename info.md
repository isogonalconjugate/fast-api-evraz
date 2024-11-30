```bash
├── Dockerfile.backend
├── Dockerfile.frontend
├── app
│   ├── api
│   │ └── v1
│   │       └── endpoints
│   │           ├── __init__.py
│   │           └── router.py
│   ├── core
│   │   ├── analysis
│   │   │   ├── __init__.py
│   │   │   └── tree_parser.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── utils
│   │       ├── __init__.py
│   │       ├── pdf_generator.py
│   │       └── unzip.py
│   ├── llm_prompts
│   │   ├── errors_list.json
│   │   └── prompts.json
│   ├── main.py
│   └── services
│       └── llm_integration.py
├── config.toml
├── docker-compose.yml
├── front.py
├── logs
├── output.txt
├── requirements.txt
└── tests
    ├── integration
    └── unit
```

### Общее описание проекта

Проект представляет собой систему для анализа кода студентов, основанную на загрузке zip-архива с кодом студента, автоматической проверке структуры проекта, синтаксиса, оформления, а также на анализе кода с использованием локальной языковой модели (LLM). Система включает в себя бэкенд для обработки данных и фронтенд на базе Grafana, предоставляющий интерфейс для загрузки архивов и отображения результатов анализа.

### Основные модули проекта

#### **1. API**
Модуль предназначен для взаимодействия с внешним миром через REST API. Основные задачи:
- Обработка запросов на загрузку zip-архива.
- Возврат результатов анализа.
- Реализация маршрутов в `app/api/v1/endpoints/router.py`.

#### **2. Core**
Центральный модуль системы, отвечающий за внутреннюю логику обработки и анализа данных. Включает следующие компоненты:
- **Config** (`core/config.py`): Конфигурация приложения, в том числе загрузка переменных окружения.
- **Logger** (`core/logger.py`): Настройка логирования, используется для ведения логов системы.
- **Utils** (`core/utils`): Утилитарные функции:
  - **Unzip** (`unzip.py`): Разархивирование загружаемого zip-файла.
  - **PDF Generator** (`pdf_generator.py`): Генерация отчетов о проверках в формате PDF.
- **Analysis** (`core/analysis/tree_parser.py`): Анализ структуры проекта, включая построение дерева файлов и папок.

#### **3. LLM Prompts**
Модуль для работы с локальной языковой моделью. Содержит подготовленные промпты и список ошибок для автоматизации проверки кода:
- `prompts.json`: Шаблоны запросов для анализа кода.
- `errors_list.json`: Список возможных ошибок и их описания для проверки структуры и оформления.

#### **4. Services**
Модуль, реализующий взаимодействие с локальной LLM. Основные задачи:
- Формирование запросов к LLM.
- Получение и обработка ответов от модели.
- Логика работы описана в `services/llm_integration.py`.

#### **5. Logs**
Папка для хранения логов работы приложения, помогает в мониторинге и отладке.

#### **6. Tests**
Модуль для тестирования:
- **Unit-тесты** (`tests/unit`): Тестирование отдельных функций.
- **Интеграционные тесты** (`tests/integration`): Проверка работы системы в целом.

#### **7. Docker и Docker Compose**
- `Dockerfile.backend` и `Dockerfile.frontend`: Конфигурация Docker для развертывания бэкенда и фронтенда.
- `docker-compose.yml`: Конфигурация для одновременного запуска всех компонентов системы.

#### **8. Config**
- `config.toml`: Настройки системы, включая параметры для подключения к LLM, базы данных, и другие конфигурации.

#### **9. Frontend**
- `front.py`: Вспомогательный файл для настройки и интеграции Grafana с бэкендом.

#### **10. Output**
- `output.txt`: Файл для сохранения временных или тестовых данных.

#### **11. Requirements**
- `requirements.txt`: Список необходимых зависимостей Python для работы приложения.

### Основные этапы обработки

1. **Загрузка данных**:
   - Пользователь загружает zip-архив с кодом через интерфейс Grafana.
   - Архив передается на бэкенд.

2. **Обработка на бэкенде**:
   - Разархивирование zip-файла.
   - Анализ структуры проекта с использованием `tree_parser.py`.
   - Сохранение данных о коде и структуре проекта в базу.

3. **Анализ кода**:
   - Проверка структуры, оформления и содержания кода с использованием LLM и программных инструментов (`flake8`, `isort` и т.д.).
   - Формирование отчета и ошибок.

4. **Вывод результатов**:
   - Генерация отчета в PDF.
   - Отправка данных на фронтенд для отображения в Grafana.

Этот проект структурирован таким образом, чтобы обеспечить масштабируемость, удобство тестирования и возможности для дальнейшего расширения функциональности. Если нужно что-то уточнить или доработать, дайте знать!

```python
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
        self.logs = config.get('logs', 'logs/app.log')


class LoggingConfig:
    def __init__(self, config):
        self.level = config.get('level', 'INFO').upper()
        self.file = config.get('file', 'logs/app.log')
        self.format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.max_bytes = config.get('max_bytes', 10485760)  # 10 MB
        self.backup_count = config.get('backup_count', 5)


class Config:
    def __init__(self, config_file='config.toml'):
        self.config_file = Path(config_file)
        if not self.config_file.exists():
            raise FileNotFoundError(f"Конфигурационный файл {config_file} не найден.")
        self.config = toml.load(self.config_file)

        # Инициализация вложенных конфигураций
        self.llm = LLMConfig(self.config.get('llm', {}))
        self.paths = PathsConfig(self.config.get('paths', {}))
        self.logging = LoggingConfig(self.config.get('logging', {}))

    def get(self, section, key, default=None):
        """Получение значения из конфигурации по секции и ключу."""
        return self.config.get(section, {}).get(key, default)-e \n\n
```
```python
# app/core/analysis/tree_parser.py

import os
# В любом другом модуле, например, tree_parser.py
import logging

logger = logging.getLogger(__name__)


def parse_project_tree(root_dir):
    logger.info(f"Начало анализа дерева проекта: {root_dir}")
    project_tree = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        rel_path = os.path.relpath(dirpath, root_dir)
        project_tree[rel_path] = {
            'directories': dirnames,
            'files': filenames
        }
    return project_tree


def check_structure(project_tree, requirements):
    # Реализовать проверку структуры проекта на соответствие требованиям
    pass

```
```python
# app/core/utils/unzip.py

import zipfile
import os

def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
```
```python
# app/core/utils/pdf_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.enums import TA_LEFT
import logging


def generate_pdf_report(analysis_result: str) -> bytes:
    """
    Генерирует PDF-отчет на основе результатов анализа.

    :param analysis_result: Строка с результатами анализа от LLM.
    :return: PDF-отчет в виде байтов.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT, fontSize=12, leading=15))

    # Заголовок
    title = Paragraph("Отчет по анализу кода", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Разделение результатов на ошибки
    errors = analysis_result.split("\n\n")  # Предполагаем, что ошибки разделены двойными переносами

    for error in errors:
        if not error.strip():
            continue  # Пропускаем пустые строки
        # Разделение на части: описание ошибки, код, предложение
        # Предполагаем, что каждая ошибка содержит:
        # - Описание ошибки
        # - Блок кода
        # - Предложение по улучшению

        # Можно использовать регулярные выражения или иной способ разделения
        # Здесь используем простой разделитель "---"

        parts = error.split('---')
        if len(parts) < 3:
            continue  # Не соответствует ожидаемому формату

        description = parts[0].strip()
        code_block = parts[1].strip()
        suggestion = parts[2].strip()

        # Добавляем описание ошибки
        desc_paragraph = Paragraph(f"<b>Ошибка:</b> {description}", styles['Left'])
        elements.append(desc_paragraph)
        elements.append(Spacer(1, 6))

        # Добавляем блок кода
        code_paragraph = Paragraph(f"<b>Код:</b><br/><pre>{code_block}</pre>", styles['Left'])
        elements.append(code_paragraph)
        elements.append(Spacer(1, 6))

        # Добавляем предложение по улучшению
        suggestion_paragraph = Paragraph(f"<b>Предложение:</b> {suggestion}", styles['Left'])
        elements.append(suggestion_paragraph)
        elements.append(Spacer(1, 12))

    # Строим PDF
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
```
```python
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


```

app/llm_prompts/errors_list.json
```json
[
    "Структурные ошибки: Неверная структура директорий",
    "Отсутствие обязательных папок (components, docs, deployment)",
    "Несоответствие именования директорий",
    "Отсутствие конфигурационных файлов (.gitignore, .editorconfig, .gitattributes)",
    "Код не соответствует PEP8",
    "Несоответствие докстрингов стандартам PEP256 и PEP257",
    "Использование print вместо logging",
    "Отсутствие тестов",
    "Неверное именование тестовых файлов и функций",
    "Некорректная работа с базой данных",
    "Неправильная обработка дат и времени",
    "Отсутствие документации"
]
```
app/llm_prompts/prompts.json
```json
{
    "code_analysis_prompt": "Проанализируй следующий код на наличие следующих потенциальных ошибок:\n\n{code}\n\nОшибки для проверки:\n{errors}\n\nПредоставь список найденных ошибок, каждый с блоком кода, показывающим проблемный участок, и предложениями по улучшению с измененным кодом."
}
```

```python
# app/api/v1/endpoints/router.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import shutil
import os
from app.core.utils.unzip import unzip_file
from app.core.analysis.tree_parser import parse_project_tree
from app.core.config import Config
from app.services.llm_model import LLMIntegration
from app.core.logger import logger
from app.core.utils.pdf_generator import generate_pdf_report
import json
from io import BytesIO

router = APIRouter()
config = Config()


@router.post("/upload")
async def upload_zip(file: UploadFile = File(...)):
   logger.info(f"Получен файл: {file.filename}")
   temp_dir = config.paths.unzip_dir
   os.makedirs(temp_dir, exist_ok=True)
   zip_path = os.path.join(temp_dir, file.filename)

   # Сохраняем загруженный файл
   try:
      with open(zip_path, "wb") as buffer:
         shutil.copyfileobj(file.file, buffer)
      logger.info(f"Файл сохранен по пути: {zip_path}")
   except Exception as e:
      logger.error(f"Ошибка при сохранении файла: {e}")
      raise HTTPException(status_code=500, detail="Ошибка сервера")

   # Разархивируем файл
   extract_to = os.path.join(temp_dir, os.path.splitext(file.filename)[0])
   try:
      unzip_file(zip_path, extract_to)
      logger.info(f"Файл разархивирован в: {extract_to}")
   except Exception as e:
      logger.error(f"Ошибка при разархивировании файла: {e}")
      raise HTTPException(status_code=400, detail="Некорректный ZIP-файл")

   # Анализируем структуру проекта
   try:
      project_tree = parse_project_tree(extract_to)
      logger.debug(f"Дерево проекта: {project_tree}")
   except Exception as e:
      logger.error(f"Ошибка при анализе дерева проекта: {e}")
      raise HTTPException(status_code=500, detail="Ошибка сервера")

   # Загрузка файлов для анализа
   code_texts = []
   binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.exe', '.dll', '.so', '.class', '.jar']
   for root, dirs, files in os.walk(extract_to):
      for filename in files:
         file_path = os.path.join(root, filename)
         if any(filename.lower().endswith(ext) for ext in binary_extensions):
            logger.debug(f"Пропускаем бинарный файл: {file_path}")
            continue
         try:
            with open(file_path, 'r', encoding='utf-8') as f:
               content = f.read()
               code_texts.append(f"---\nФайл: {file_path}\n---\n{content}")
         except (UnicodeDecodeError, PermissionError) as e:
            logger.warning(f"Не удалось прочитать файл {file_path}: {e}")
            continue

   combined_code = "\n\n".join(code_texts)
   logger.info("Собранный код из всех читаемых файлов.")

   # Загрузка промпта для LLM
   try:
      with open(config.paths.prompts, 'r', encoding='utf-8') as f:
         prompts = json.load(f)
      prompt_template = prompts.get('code_analysis_prompt', '')
   except Exception as e:
      logger.error(f"Ошибка при загрузке промптов: {e}")
      raise HTTPException(status_code=500, detail="Ошибка сервера")

   # Загрузка списка потенциальных ошибок из JSON файла
   try:
      with open(config.paths.errors_list, 'r', encoding='utf-8') as f:
         errors_list = json.load(f)
      # Проверка, что errors_list является списком строк
      if not isinstance(errors_list, list) or not all(isinstance(err, str) for err in errors_list):
         logger.error("Некорректный формат errors_list.json")
         raise HTTPException(status_code=500, detail="Ошибка сервера")
      # Преобразуем список ошибок в строку
      errors = '\n'.join(errors_list)
      logger.info("Список ошибок загружен из JSON файла.")
   except Exception as e:
      logger.error(f"Ошибка при загрузке списка ошибок: {e}")
      raise HTTPException(status_code=500, detail="Ошибка сервера")

   # Формируем промпт
   prompt = prompt_template.format(code=combined_code, errors=errors)
   logger.debug("Сформирован промпт для LLM.")

   # Инициализация LLM
   try:
      llm = LLMIntegration(model_name=config.llm.model_name)
   except Exception as e:
      logger.error(f"Ошибка при инициализации LLM: {e}")
      raise HTTPException(status_code=500, detail="Ошибка сервера")

   # Анализ кода
   try:
      analysis_result = llm.analyze_code(prompt)
      logger.info("Анализ кода завершен.")
   except Exception as e:
      logger.error(f"Ошибка во время анализа кода: {e}")
      raise HTTPException(status_code=500, detail="Ошибка сервера")

   # Генерация PDF отчета
   try:
      pdf_bytes = generate_pdf_report(analysis_result)
      logger.info("PDF отчет успешно сгенерирован.")
   except Exception as e:
      logger.error(f"Ошибка при генерации PDF отчета: {e}")
      raise HTTPException(status_code=500, detail="Ошибка при генерации отчета")

   # Создание объекта BytesIO для отправки файла
   pdf_file = BytesIO(pdf_bytes)
   pdf_file.seek(0)

   logger.info("Отправка PDF отчета клиенту.")

   # Возвращаем PDF как StreamingResponse
   return StreamingResponse(
      pdf_file,
      media_type="application/pdf",
      headers={
         "Content-Disposition": f"attachment; filename=report_{os.path.splitext(os.path.basename(file.filename))[0]}.pdf"}
   )
```
```python
# app/main.py

from fastapi import FastAPI
from app.api.v1.endpoints.router import router as api_router
from app.core.logger import logger

app = FastAPI(title="Code Analyzer")

@app.on_event("startup")
async def startup_event():
    logger.info("Приложение запущено.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Приложение остановлено.")

app.include_router(api_router, prefix="/api/v1")
```
```python
# app/services/llm_integration.py

import subprocess
from app.core.logger import logger

class LLMIntegration:
    def __init__(self, model_name):
        self.model_name = model_name
        logger.info(f"LLMIntegration инициализирован с моделью: {self.model_name}")

    def analyze_code(self, prompt):
        logger.debug("Начало анализа кода с помощью LLM.")
        try:
            process = subprocess.Popen(
                ['ollama', 'run', self.model_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  # Линейно буферизованный вывод
            )

            # Отправка промпта в stdin Ollama
            logger.info(f"PROMPT: {prompt}")
            process.stdin.write(prompt)
            process.stdin.close()

            # Чтение вывода построчно и логирование
            analysis_output = []
            for line in process.stdout:
                cleaned_line = line.strip()
                if cleaned_line:  # Пропускаем пустые строки
                    logger.info(f"LLM: {cleaned_line}")
                    analysis_output.append(line)

            process.wait()
            if process.returncode != 0:
                error_output = ''.join(analysis_output)
                logger.error(f"LLM вернула ошибку: {error_output}")
                raise Exception(f"LLM Error: {error_output}")

            logger.debug("Анализ LLM завершен успешно.")
            return ''.join(analysis_output)
        except Exception as e:
            logger.error(f"Ошибка во время работы LLM: {e}")
            raise

```

requirements.txt
```txt
fastapi
uvicorn
toml
requests
python-multipart
reportlab
gradio


```
```dockerfile
# Dockerfile.backend

# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Копируем только файлы зависимостей для кеширования
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальную часть приложения
COPY app/ ./app/
COPY config.toml ./

# Создаем директорию для логов
RUN mkdir -p logs

# Устанавливаем переменную окружения для FastAPI
ENV PYTHONUNBUFFERED=1

# Экспонируем порт FastAPI
EXPOSE 8000

# Запускаем FastAPI с помощью Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

```
```yml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: fastapi_backend
    restart: always
    volumes:
      - ./app:/usr/src/app/app
      - ./config.toml:/usr/src/app/config.toml
      - ./logs:/usr/src/app/logs
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: gradio_frontend
    restart: always
    volumes:
      - ./front.py:/usr/src/app/front.py
      - ./config.toml:/usr/src/app/config.toml
    ports:
      - "7860:7860"
    environment:
      - PYTHONUNBUFFERED=1
    depends_on:
      - backend


```
```toml
[llm]
model_name = "qwen2.5-coder:3b"

[paths]
unzip_dir = "temp_unzipped"
prompts = "app/llm_prompts/prompts.json"
errors_list = "app/llm_prompts/errors_list.json"
logs = "logs/app.log"

[logging]
level = "INFO"
file = "logs/app.log"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
max_bytes = 10485760  # 10 MB
backup_count = 5
```
```python
import gradio as gr
import requests
import os
from io import BytesIO

# Обновленный эндпоинт FastAPI
API_URL = "http://localhost:8000/api/v1/upload"


def upload_and_analyze(file):
    if file is None:
        return "❌ Нет загруженного файла.", None

    try:
        # Отправляем файл на FastAPI
        with open(file.name, "rb") as f:  # `file` - это объект File из Gradio
            files = {'file': (os.path.basename(file.name), f, 'application/zip')}
            response = requests.post(API_URL, files=files)

        if response.status_code != 200:
            return f"❌ Ошибка при обработке файла: {response.text}", None

        # Получаем PDF-отчет
        pdf_content = response.content

        # Создаем объект BytesIO
        pdf_file = BytesIO(pdf_content)
        pdf_file.name = f"report_{os.path.splitext(os.path.basename(file.name))[0]}.pdf"
        pdf_file.seek(0)

        return "✅ Файл успешно обработан. Скачать отчет ниже.", pdf_file

    except Exception as e:
        return f"❌ Произошла ошибка: {str(e)}", None


# Создание интерфейса Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 🗂️ Анализатор Файлов и Структуры Проекта")
    gr.Markdown("Загрузите ZIP-архив для анализа.")

    with gr.Row():
        file_input = gr.File(label="Загрузите ZIP-архив", file_types=[".zip"], type="filepath")

    analyze_button = gr.Button("Анализировать")

    status_output = gr.Textbox(label="Статус", interactive=False)
    pdf_output = gr.File(label="Скачать PDF отчет", interactive=False)

    analyze_button.click(
        upload_and_analyze,
        inputs=file_input,
        outputs=[status_output, pdf_output]
    )

if __name__ == "__main__":
    demo.launch()
    
```
```dockerfile
# Dockerfile.frontend

# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Копируем только файлы зависимостей для кеширования
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем фронтенд код
COPY front.py ./
COPY config.toml ./

# Устанавливаем переменную окружения для Gradio (опционально)
ENV PYTHONUNBUFFERED=1

# Экспонируем порт Gradio
EXPOSE 7860

# Запускаем Gradio фронтенд
CMD ["python", "front.py"]
```


