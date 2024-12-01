import ollama
import os
import json
from app.core.logger import logger
from app.core.utils.code_analysis import (
    get_file_content_with_line_numbers,
    search_in_files,
    check_pep8_compliance,
    format_project_tree
)


class LLMModel:
    def __init__(self, model_name):
        self.model_name = model_name
        logger.info(f"LLMModel инициализирован с моделью: {self.model_name}")

    def analyze_rule(self, rule):
        # Получаем дерево проекта
        project_tree = format_project_tree()

        # Загрузка системного промпта для первой модели
        system_prompt = self.load_prompt('first_model_prompt.txt')

        # Подготовка сообщений для первой модели
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Правило:\n{rule}\n\nДерево проекта:\n{project_tree}"}
        ]

        # Логируем промпты
        logger.info(f"Промпты перед вызовом первой модели:\n{json.dumps(messages, ensure_ascii=False, indent=2)}")

        # Определение доступных функций
        available_functions = {
            'file_content': self.file_content,
            'search_files': self.search_files,
            'check_pep8': self.check_pep8
        }

        # Подготовка инструментов для ollama
        tools = [self.get_function_definition(func_name, func) for func_name, func in available_functions.items()]

        # Запуск первой модели с потоковой передачей
        response_generator = ollama.chat(
            model=self.model_name,
            messages=messages,
            tools=tools,
            max_tokens=2048,
            stream=True
        )

        # Отображение ответа модели в реальном времени
        first_model_output = self.display_stream_response(response_generator)

        # Обработка вызовов функций
        if hasattr(response_generator, 'tool_calls') and response_generator.tool_calls:
            for tool in response_generator.tool_calls:
                func_name = tool.function.name
                func_args = tool.function.arguments
                func = available_functions.get(func_name)
                if func:
                    logger.info(f"Вызов функции: {func_name} с аргументами {func_args}")
                    output = func(**func_args)
                    logger.info(f"Вывод функции {func_name}:\n{output[:500]}...")

                    messages.append({'role': 'assistant', 'content': first_model_output})
                    messages.append({'role': 'tool', 'content': output, 'name': func_name})

                    # Логируем обновленные промпты
                    logger.info(f"Промпты перед повторным вызовом первой модели:\n{json.dumps(messages, ensure_ascii=False, indent=2)}")

                    # Повторный запуск модели с новым сообщением
                    response_generator = ollama.chat(
                        model=self.model_name,
                        messages=messages,
                        tools=tools,
                        max_tokens=2048,
                        stream=True
                    )

                    # Отображение ответа модели в реальном времени
                    first_model_output = self.display_stream_response(response_generator)
                else:
                    logger.warning(f"Функция {func_name} не найдена.")
        else:
            logger.info("Модель не вызвала никаких функций.")

        # Запуск второй модели
        second_model_output = self.run_second_model(first_model_output)

        # Запуск третьей модели
        passed = self.run_third_model(second_model_output)

        # Возврат результата
        if not passed:
            return second_model_output
        else:
            return None

    def run_second_model(self, first_model_output):
        # Загрузка системного промпта для второй модели
        system_prompt = self.load_prompt('second_model_prompt.txt')
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': first_model_output}
        ]

        # Логируем промпты
        logger.info(f"Промпты перед вызовом второй модели:\n{json.dumps(messages, ensure_ascii=False, indent=2)}")

        response_generator = ollama.chat(
            model=self.model_name,
            messages=messages,
            max_tokens=2048,
            stream=True
        )

        # Отображение ответа модели в реальном времени
        second_model_output = self.display_stream_response(response_generator)
        return second_model_output

    def run_third_model(self, second_model_output):
        # Загрузка системного промпта для третьей модели
        system_prompt = self.load_prompt('third_model_prompt.txt')
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': second_model_output}
        ]

        # Логируем промпты
        logger.info(f"Промпты перед вызовом третьей модели:\n{json.dumps(messages, ensure_ascii=False, indent=2)}")

        response_generator = ollama.chat(
            model=self.model_name,
            messages=messages,
            max_tokens=512,
            stream=True
        )

        # Отображение ответа модели в реальном времени
        third_model_output = self.display_stream_response(response_generator)

        try:
            result = json.loads(third_model_output)
            return result.get('passed', True)
        except json.JSONDecodeError:
            logger.error("Ответ третьей модели не является валидным JSON.")
            return True  # Считаем, что проверка пройдена, если JSON некорректен

    def display_stream_response(self, response_generator):
        output = ""
        print("Ответ модели:")
        for chunk in response_generator:
            print(chunk, end='', flush=True)
            output += chunk
        print()  # Перенос строки после завершения ответа
        return output

    def load_prompt(self, filename):
        prompt_path = os.path.join('app', 'llm_prompts', filename)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_function_definition(self, name, func):
        return {
            'type': 'function',
            'function': {
                'name': name,
                'description': func.__doc__,
                'parameters': self.get_function_parameters(func),
            }
        }

    def get_function_parameters(self, func):
        # Используем аннотации функций для определения параметров
        params = {}
        for param_name, param_type in func.__annotations__.items():
            params[param_name] = {'type': 'string', 'description': ''}
        return {
            'type': 'object',
            'properties': params,
        }

    # Реализация функций, которые может вызывать модель

    def file_content(self, paths: list, extension_filter: str = None, max_lines_per_file: int = 600) -> str:
        """
        Получить содержимое файлов по заданным путям с нумерацией строк и форматированием.
        """
        return get_file_content_with_line_numbers(paths, extension_filter, max_lines_per_file)

    def search_files(self, term: str, extension_filter: str = None, regular: bool = False, max_results: int = 5) -> str:
        """
        Поиск термина в файлах проекта с выводом контекста и нумерацией строк.
        """
        return search_in_files(term, extension_filter, regular, max_results)

    def check_pep8(self, max_errors: int = 5) -> str:
        """
        Проверка кода на соответствие PEP8 с выводом ошибок и нумерацией строк.
        """
        return check_pep8_compliance(max_errors)
