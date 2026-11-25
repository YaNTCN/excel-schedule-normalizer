"""Выгрузка результата в Excel, CSV и JSON."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from .model import WEEK_NAMES, Result

COLUMNS = (
    ("group", "Группа"),
    ("weekday", "День"),
    ("start", "Начало"),
    ("end", "Конец"),
    ("week", "Неделя"),
    ("subject", "Дисциплина"),
    ("type", "Вид"),
    ("teacher", "Преподаватель"),
    ("room", "Аудитория"),
    ("source", "Откуда"),
)
ISSUE_COLUMNS = (("kind", "Что"), ("message", "Описание"), ("source", "Где"))


def rows(result: Result) -> list[dict]:
    return [
        {
            "group": lesson.group,
            "weekday": lesson.weekday_name,
            "start": lesson.start or "",
            "end": lesson.end or "",
            "week": WEEK_NAMES[lesson.week],
            "subject": lesson.subject,
            "type": lesson.type,
            "teacher": lesson.teacher,
            "room": lesson.room,
            "source": lesson.source,
        }
        for lesson in result.lessons
    ]


def save(result: Result, path: str | Path) -> None:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        _save_xlsx(result, path)
    elif suffix == ".csv":
        _save_csv(result, path)
    elif suffix == ".json":
        _save_json(result, path)
    else:
        raise ValueError(f"не умею сохранять в {suffix or 'файл без расширения'}: нужен .xlsx, .csv или .json")


def _save_xlsx(result: Result, path: Path) -> None:
    book = Workbook()
    _sheet(book.active, "Расписание", COLUMNS, rows(result))
    issues = [{"kind": i.kind, "message": i.message, "source": i.source} for i in result.issues]
    _sheet(book.create_sheet(), "Замечания", ISSUE_COLUMNS, issues)
    book.save(path)


def _sheet(sheet, title: str, columns, data: list[dict]) -> None:
    sheet.title = title
    sheet.append([label for _, label in columns])
    for item in data:
        sheet.append([item[key] for key, _ in columns])
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDEBF7")
    for index, (key, label) in enumerate(columns, start=1):
        longest = max([len(label)] + [len(str(item[key])) for item in data])
        sheet.column_dimensions[get_column_letter(index)].width = min(longest + 2, 60)
    sheet.freeze_panes = "A2"
    if data:
        sheet.auto_filter.ref = sheet.dimensions


def _save_csv(result: Result, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=[key for key, _ in COLUMNS], delimiter=";")
        writer.writeheader()
        writer.writerows(rows(result))


def _save_json(result: Result, path: Path) -> None:
    data = {
        "lessons": rows(result),
        "issues": [{"kind": i.kind, "message": i.message, "source": i.source} for i in result.issues],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
