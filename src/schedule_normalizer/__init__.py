"""Сводит расписания из Excel-файлов разного вида в одну таблицу."""

from .model import Issue, Lesson, Result
from .normalize import normalize, normalize_file

__all__ = ["Issue", "Lesson", "Result", "normalize", "normalize_file"]
__version__ = "0.1.0"
