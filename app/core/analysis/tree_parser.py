# app/core/analysis/tree_parser.py

import os
# В любом другом модуле, например, tree_parser.py
import logging

logger = logging.getLogger(__name__)


def parse_project_tree(root_dir):
    logger.info(f"Начало анализа дерева проекта: {root_dir}")
    project_tree = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        rel_path = os.path.relpath(dirpath, root_dir)
        project_tree[rel_path] = {
            'directories': dirnames,
            'files': filenames
        }
    return project_tree


def check_structure(project_tree, requirements):
    # Реализовать проверку структуры проекта на соответствие требованиям
    pass
