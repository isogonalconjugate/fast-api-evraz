# app/api/v1/endpoints/router.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import shutil
import os
from app.core.utils.unzip import unzip_file
from app.core.analysis.tree_parser import parse_project_tree
from app.core.config import Config
from app.services.llm_integration import LLMIntegration
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
