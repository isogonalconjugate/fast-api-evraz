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