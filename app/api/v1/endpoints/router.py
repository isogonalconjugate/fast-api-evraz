# app/api/v1/endpoints/router.py
from fastapi import BackgroundTasks
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import shutil
import os
import json
from io import BytesIO
from app.core.utils.unzip import unzip_file
from app.core.config import Config
from app.services.llm_model import LLMModel
from app.core.logger import logger
from app.core.utils.pdf_generator import generate_pdf_report
from app.core.utils.code_analysis import format_project_tree

router = APIRouter()
config = Config()


@router.post("/upload")
async def upload_zip(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
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
        raise HTTPException(status_code=500, detail="Ошибка сервера при сохранении файла.")

    # Разархивируем файл
    extract_to = os.path.join(temp_dir, os.path.splitext(file.filename)[0])
    try:
        unzip_file(zip_path, extract_to)
        logger.info(f"Файл разархивирован в: {extract_to}")
    except Exception as e:
        logger.error(f"Ошибка при разархивировании файла: {e}")
        raise HTTPException(status_code=400, detail="Некорректный ZIP-файл.")

    # Устанавливаем project_root в конфигурации
    config.set_project_root(extract_to)

    # Инициализируем LLMModel без передачи project_root
    llm_model = LLMModel(model_name=config.llm.model_name)

    # Загрузка правил из rules.json
    try:
        with open(config.paths.rules, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        logger.info("Правила загружены из rules.json.")
    except Exception as e:
        logger.error(f"Ошибка при загрузке правил: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при загрузке правил.")

    # Получение дерева проекта в виде строки
    project_tree_str = format_project_tree()

    # Инициализация списка для хранения результатов анализа
    analysis_results = []

    # Обработка каждого правила
    for rule_obj in rules:
        rule = rule_obj['rule']
        logger.info(f"Анализ правила: {rule}")
        analysis_result = llm_model.analyze_rule(rule)
        if analysis_result:
            analysis_results.append(analysis_result)

    # Проверяем, есть ли результаты анализа
    if not analysis_results:
        return {"detail": "Ошибок не обнаружено."}

    # Генерация PDF отчета на основе результатов анализа
    try:
        pdf_bytes = generate_pdf_report('\n\n'.join(analysis_results))
        logger.info("PDF отчет успешно сгенерирован.")
    except Exception as e:
        logger.error(f"Ошибка при генерации PDF отчета: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при генерации отчета.")

    # Отправка PDF отчета клиенту
    pdf_file = BytesIO(pdf_bytes)
    pdf_file.seek(0)

    background_tasks.add_task(cleanup_temp_dirs, extract_to)

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{os.path.splitext(os.path.basename(file.filename))[0]}.pdf"}
    )


def cleanup_temp_dirs(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        logger.info(f"Deleted: {path}")
    except Exception as e:
        logger.error(f"Error deleting {path}: {e}")
