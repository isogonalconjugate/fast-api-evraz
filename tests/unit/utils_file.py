from app.core.utils.code_analysis import (
    get_file_content_with_line_numbers,
    search_in_files,
    check_pep8_compliance)

# print(get_file_content_with_line_numbers(
#    ["app/core/utils/code_analysis.py"],
#    ".py"))

# print(search_in_files(
#     ["print"],
#     max_results=15
#     ))

print(check_pep8_compliance(max_errors=10))
