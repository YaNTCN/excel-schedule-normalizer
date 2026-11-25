"""Список: одна строка на пару, у каждого столбца своя шапка.

Так выгружают из учётных систем и так ведут расписание колледжи.
Типичный мусор: шапка повторяется посреди листа, пустые строки, итоги,
день недели пишут только в первой строке дня, в одной ячейке несколько групп.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import cells, times, vocab
from ..grid import Grid
from ..model import Issue, Lesson, Result

NAME = "список"
REQUIRED = {"group", "weekday", "subject"}


@dataclass
class Layout:
    header: int
    columns: dict[str, int]


def detect(grid: Grid) -> Layout | None:
    for row in range(min(grid.height, 30)):
        columns: dict[str, int] = {}
        for col in range(grid.width):
            role = vocab.column_role(grid.value(row, col))
            if role and role not in columns:
                columns[role] = col
        if REQUIRED <= columns.keys() and ({"time", "start"} & columns.keys()):
            return Layout(row, columns)
    return None


def extract(grid: Grid, layout: Layout) -> Result:
    result = Result(sheets=1)
    header_text = grid.rows[layout.header]
    day_by_group: dict[str, int] = {}

    def value(row: int, role: str) -> str:
        column = layout.columns.get(role)
        return grid.value(row, column) if column is not None else ""

    for row in range(layout.header + 1, grid.height):
        if grid.row_is_empty(row) or grid.rows[row] == header_text:
            continue
        groups = vocab.groups_in(value(row, "group"))
        subject_text = value(row, "subject")
        if not groups or not subject_text:
            continue
        where = grid.where(row, layout.columns["subject"])

        day_text = value(row, "weekday")
        day = vocab.weekday(day_text)
        if day is None and day_text:
            result.issues.append(Issue("день", f"не понял день недели «{day_text}», строка пропущена", where))
            continue
        day = day or day_by_group.get(groups[0])
        if day is None:
            result.issues.append(Issue("день", "нет дня недели, строка пропущена", where))
            continue

        time = _time(value(row, "time"), value(row, "start"), value(row, "end"))
        if time is None:
            written = value(row, "time") or value(row, "start")
            message = f"не понял время «{written}»" if written else "нет времени"
            result.issues.append(Issue("время", message, where))
        elif times.is_reversed(time):
            result.issues.append(Issue("время", f"конец пары раньше начала: {value(row, 'time')}", where))

        subject, week = cells.split_week(subject_text)
        if value(row, "week"):
            week = cells.week_value(value(row, "week"))
        teacher = cells.teacher_name(value(row, "teacher"))
        start, end = time if time else (None, None)
        for group in groups:
            day_by_group[group] = day
            result.lessons.append(Lesson(
                group, day, start, end, subject, vocab.lesson_type(value(row, "type")),
                teacher, cells.room_name(value(row, "room")), week, where,
            ))
    return result


def _time(time: str, start: str, end: str) -> times.TimeRange | None:
    if time:
        return times.parse_time(time)
    begin, finish = times.parse_time(start), times.parse_time(end)
    if begin is None:
        return None
    return begin[0], finish[0] if finish else None
