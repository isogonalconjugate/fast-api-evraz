from app.core.utils.code_analysis import (
    get_file_content_with_line_numbers,
    search_in_files)

print(get_file_content_with_line_numbers(
    ["app/core/utils/code_analysis.py"],
    ".py"))

print(search_in_files(
    "print",
    ))
