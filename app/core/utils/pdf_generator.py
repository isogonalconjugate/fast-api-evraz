import markdown
import pdfkit
import os
from app.core.logger import logger
from app.core.config import Config


def generate_pdf_report(md_content: str) -> bytes:
    """
    Конвертирует строку в формате Markdown в PDF и возвращает PDF в виде байтов.
    При этом сохраняются стилистические элементы, такие как блоки кода, цитаты и прочее.

    :param md_content: Строка в формате Markdown.
    :return: PDF-отчет в виде байтов.
    """
    # Получаем конфигурацию из config.toml
    config = Config()
    wkhtmltopdf_path = config.pdf.wkhtmltopdf_path

    # Проверяем наличие wkhtmltopdf
    if not os.path.exists(wkhtmltopdf_path):
        logger.error(f"wkhtmltopdf не найден по пути: {wkhtmltopdf_path}")
        raise FileNotFoundError(f"wkhtmltopdf не найден по пути: {wkhtmltopdf_path}")

    # Конфигурация для pdfkit
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Стили для улучшенного отображения
    css = '''
    @font-face {
        font-family: "Liberation Sans";
        src: local("Liberation Sans"), local("DejaVu Sans");
    }
    body {
        font-family: "Liberation Sans", "Arial", sans-serif;
        font-size: 12pt;
        line-height: 1.5;
        word-wrap: break-word;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #333;
        font-weight: bold;
    }
    h1 {
        font-size: 24pt;
    }
    h2 {
        font-size: 20pt;
    }
    h3 {
        font-size: 18pt;
    }
    pre, code {
        background-color: #f4f4f4;
        padding: 10px;
        border-radius: 5px;
        font-family: "Courier New", Courier, monospace;
        font-size: 9pt;
        overflow-x: auto;
    }
    blockquote {
        background-color: #f0f0f0;
        border-left: 5px solid #ccc;
        padding: 10px 15px;
        margin: 10px 0;
        font-style: italic;
    }
    ul, ol {
        margin: 10px 0;
        padding-left: 20px;
    }
    li {
        margin: 5px 0;
    }
    '''
    css_file = 'temp_style.css'
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css)

    # Конвертируем строку Markdown в HTML
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])

    # Добавляем явное указание кодировки для HTML
    html_content = f'<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Отчет по анализу кода</title></head><body>{html_content}</body></html>'

    try:
        # Конвертируем HTML в PDF
        pdf_bytes = pdfkit.from_string(html_content, False, configuration=pdfkit_config, css=css_file)
    except Exception as e:
        logger.error(f"Ошибка при конвертации HTML в PDF: {e}")
        raise

    # Удаляем временный файл CSS
    os.remove(css_file)

    return pdf_bytes
