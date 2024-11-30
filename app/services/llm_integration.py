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