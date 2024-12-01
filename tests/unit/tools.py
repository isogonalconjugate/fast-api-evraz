import ollama


# Определяем функцию для проверки кода
def check_code_for_errors(code_snippet):
    # Формируем системное сообщение, направляющее модель на возврат JSON с полем Errors
    system_message = {
        'role': 'system',
        'content': (
            "Вы являетесь ассистентом, который проверяет предоставленный участок кода на ошибки. "
            "Если ошибки обнаружены, верните JSON с 'errors': true, 'response: ответ модели'" 
            "Если ошибок нет, верните JSON с 'errors': false, 'response': ответ модели"
        )
    }

    # Формируем сообщение пользователя с предоставленным кодом
    user_message = {
        'role': 'user',
        'content': f"Проверьте следующий код на ошибки:\n\n{code_snippet}"
    }

    # Отправляем запрос к модели с системным и пользовательским сообщениями
    response = ollama.chat(
        model='qwen2.5-coder',  # Замените на нужную модель
        messages=[system_message, user_message]
    )

    # Получаем и возвращаем ответ модели
    return response['message']['content']

# Пример использования функции
code_to_check = '''
def add(a, b):
    return a + b
    def subtract(a, b):

print(add(2, 3))
'''

result = check_code_for_errors(code_to_check)
print(result)