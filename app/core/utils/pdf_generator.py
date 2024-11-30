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
