import os
import re
import json
import subprocess
from app.core.logger import logger
from app.core.config import Config

# Получаем project_root из конфигурации
config = Config()
project_root = config.paths.project_root

def get_file_content_with_line_numbers(paths, extension_filter=None, max_lines_per_file=100):
    """
    Получить содержимое файлов по заданным путям с нумерацией строк и форматированием в Markdown.
    """
    output = []
    for path in paths:
        full_path = os.path.join(project_root, path)
        if os.path.isfile(full_path):
            if extension_filter and not full_path.endswith(extension_filter):
                continue
            content = read_file_with_line_numbers(full_path, max_lines_per_file)
            if content:
                output.append(f"### {path}\n{content}")
        elif os.path.isdir(full_path):
            for root, _, files in os.walk(full_path):
                for file in files:
                    if extension_filter and not file.endswith(extension_filter):
                        continue
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_root)
                    content = read_file_with_line_numbers(file_path, max_lines_per_file)
                    if content:
                        output.append(f"### {relative_path}\n{content}")
    return '\n\n'.join(output)

def read_file_with_line_numbers(file_path, max_lines):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                truncated = True
            else:
                truncated = False
            numbered_lines = [f"{idx+1}\t{line.rstrip()}" for idx, line in enumerate(lines)]
            content = '\n'.join(numbered_lines)
            if truncated:
                content += "\n\n*...Дальше слишком много строк, вывод сокращен...*"
            return f"```\n{content}\n```"
    except Exception as e:
        logger.warning(f"Не удалось прочитать файл {file_path}: {e}")
        return None

def search_in_files(term, max_results=5):
    """
    Поиск термина в файлах проекта с выводом контекста и нумерацией строк.
    """
    results = []
    pattern = re.compile(term)
    for root, _, files in os.walk(project_root):
        for file in files:
            if not file.endswith(('.py', '.txt', '.md', '.html', '.js', '.css')):
                continue
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, project_root)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if pattern.search(line):
                            context_start = max(0, idx - 2)
                            context_end = min(len(lines), idx + 3)
                            context = lines[context_start:context_end]
                            numbered_context = [f"{i+1}\t{l.rstrip()}" for i, l in enumerate(context, start=context_start)]
                            snippet = '\n'.join(numbered_context)
                            result = f"### {relative_path}\n```\n{snippet}\n```"
                            results.append(result)
                            if len(results) >= max_results:
                                return '\n\n'.join(results) + "\n\n*...Найдено слишком много совпадений, вывод сокращен...*"
                            break  # Переходим к следующему файлу после первого совпадения
            except Exception as e:
                logger.warning(f"Не удалось прочитать файл {file_path}: {e}")
                continue
    if results:
        return '\n\n'.join(results)
    else:
        return "Совпадений не найдено."

def check_pep8_compliance(max_errors=5):
    """
    Проверка кода на соответствие PEP8 с выводом ошибок и нумерацией строк.
    """
    try:
        result = subprocess.run(
            ['flake8', project_root, '--format=%(path)s::%(row)d::%(col)d::%(code)s::%(text)s'],
            capture_output=True, text=True
        )
        if result.stdout:
            errors = result.stdout.strip().split('\n')
            output = []
            for error in errors[:max_errors]:
                path, row, col, code, text = error.split('::')
                relative_path = os.path.relpath(path, project_root)
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    idx = int(row) - 1
                    context_start = max(0, idx - 2)
                    context_end = min(len(lines), idx + 3)
                    context = lines[context_start:context_end]
                    numbered_context = [f"{i+1}\t{l.rstrip()}" for i, l in enumerate(context, start=context_start)]
                    snippet = '\n'.join(numbered_context)
                    error_output = (
                        f"### {relative_path} (Строка {row}, Столбец {col})\n"
                        f"Ошибка {code}: {text}\n"
                        f"```\n{snippet}\n```"
                    )
                    output.append(error_output)
            if len(errors) > max_errors:
                output.append("\n*...Найдено слишком много ошибок, вывод сокращен...*")
            return '\n\n'.join(output)
        else:
            return "Код соответствует PEP8."
    except Exception as e:
        logger.error(f"Ошибка при запуске flake8: {e}")
        return "Ошибка при проверке PEP8."

def format_project_tree():
    """
    Форматирует дерево проекта в виде строки.
    """
    tree_lines = []
    for root, dirs, files in os.walk(project_root):
        level = root.replace(project_root, '').count(os.sep)
        indent = ' ' * 4 * level
        tree_lines.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_lines.append(f"{subindent}{f}")
    return '\n'.join(tree_lines)
