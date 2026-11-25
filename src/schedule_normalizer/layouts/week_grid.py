"""Сетка на неделю: дни и время по строкам, группы по столбцам.

Каждая группа занимает блок столбцов от своего названия до следующей группы.
В блоке либо подписанные столбцы (дисциплина, вид, преподаватель, аудитория),
либо один столбец, где пара записана текстом.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Callable

from .. import cells, times, vocab
from ..grid import Cell, Grid
from ..model import BOTH, Issue, Lesson, Result

FIELDS = ("subject", "type", "teacher", "room")
NAME = "сетка на неделю"


@dataclass
class Block:
    group: str
    columns: dict[str, int] = field(default_factory=dict)
    text_column: int | None = None


@dataclass
class Layout:
    header: int
    first_row: int
    day_column: int
    time_column: int
    blocks: list[Block]
    issues: list[Issue] = field(default_factory=list)


def detect(grid: Grid) -> Layout | None:
    header = _group_row(grid)
    if header is None:
        return None
    day_column = _best_column(grid, header, lambda text: vocab.weekday(text) is not None)
    time_column = _best_column(grid, header, times.is_time)
    if day_column is None or time_column is None:
        return None
    labels = header + 1 if _is_label_row(grid, header + 1) else None
    blocks, issues = _blocks(grid, header, labels, {day_column, time_column})
    first_row = (labels if labels is not None else header) + 1
    return Layout(header, first_row, day_column, time_column, blocks, issues)


def extract(grid: Grid, layout: Layout) -> Result:
    result = Result(issues=list(layout.issues), sheets=1)
    seen: set[tuple[str, Cell]] = set()
    day = None
    time: times.TimeRange | None = None

    for row in range(layout.first_row, grid.height):
        if grid.row_is_empty(row):
            continue
        new_day = vocab.weekday(grid.value(row, layout.day_column))
        if new_day is not None and new_day != day:
            day, time = new_day, None
        if day is None:
            continue
        cell_time = times.parse_time(grid.value(row, layout.time_column))
        if cell_time is not None:
            if times.is_reversed(cell_time) and grid.origin(row, layout.time_column)[0] == row:
                result.issues.append(Issue(
                    "время", f"конец пары раньше начала: {grid.value(row, layout.time_column)}",
                    grid.where(row, layout.time_column),
                ))
            time = cell_time

        for block in layout.blocks:
            lesson = _lesson(grid, row, block, day, time, seen)
            if lesson is None:
                continue
            result.lessons.append(lesson)
            if time is None:
                result.issues.append(Issue("время", f"пара {lesson.subject} без времени", lesson.source))
    return result


def _lesson(grid: Grid, row: int, block: Block, day: int, time, seen) -> Lesson | None:
    column = block.text_column if block.text_column is not None else block.columns.get("subject")
    if column is None:
        return None
    text = grid.value(row, column)
    origin = grid.origin(row, column)
    # Ячейка, объединённая на две строки одной пары, это одна пара на обе недели.
    if not text or (block.group, origin) in seen:
        return None
    seen.add((block.group, origin))

    subject, week = cells.split_week(text)
    if block.text_column is not None:
        parsed = cells.parse_lesson(subject)
    else:
        values = {name: _own_value(grid, row, block, name, origin) for name in FIELDS[1:]}
        parsed = cells.Parsed(subject, vocab.lesson_type(values["type"]),
                              cells.teacher_name(values["teacher"]), cells.room_name(values["room"]))
        if _spans_other_fields(grid, row, block, origin):
            # Поток: одна широкая ячейка на несколько групп, всё записано в ней.
            parsed = cells.parse_lesson(subject)
        for name in ("type", "teacher", "room"):
            if week == BOTH and values[name]:
                week = cells.split_week(values[name])[1]

    if not parsed.subject:
        return None
    start, end = time if time else (None, None)
    return Lesson(block.group, day, start, end, parsed.subject, parsed.type,
                  parsed.teacher, parsed.room, week, grid.where(row, column))


def _own_value(grid: Grid, row: int, block: Block, name: str, subject_origin: Cell) -> str:
    column = block.columns.get(name)
    if column is None or grid.origin(row, column) == subject_origin:
        return ""
    return cells.split_week(grid.value(row, column))[0]


def _spans_other_fields(grid: Grid, row: int, block: Block, origin: Cell) -> bool:
    return any(grid.origin(row, column) == origin
               for name, column in block.columns.items() if name != "subject")


def _group_row(grid: Grid) -> int | None:
    best, best_count = None, 0
    for row in range(grid.height):
        count = sum(1 for col in range(grid.width)
                    if grid.origin(row, col) == (row, col) and vocab.groups_in(grid.value(row, col)))
        if count > best_count:
            best, best_count = row, count
    return best


def _best_column(grid: Grid, header: int, test: Callable[[str], bool]) -> int | None:
    hits = Counter()
    for row in range(header + 1, grid.height):
        for col in range(grid.width):
            if grid.origin(row, col) == (row, col) and test(grid.value(row, col)):
                hits[col] += 1
    return hits.most_common(1)[0][0] if hits else None


def _is_label_row(grid: Grid, row: int) -> bool:
    roles = {vocab.column_role(grid.value(row, col)) for col in range(grid.width)}
    return "subject" in roles


def _blocks(grid: Grid, header: int, labels: int | None, axis: set[int]) -> tuple[list[Block], list[Issue]]:
    starts = []
    for col in range(grid.width):
        if col in axis or grid.origin(header, col) != (header, col):
            continue
        if found := vocab.groups_in(grid.value(header, col)):
            starts.append((col, found[0]))

    blocks, issues = [], []
    for index, (start, group) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else grid.width
        columns = [col for col in range(start, end) if col not in axis]
        block = Block(group)
        if labels is not None:
            for col in columns:
                role = vocab.column_role(grid.value(labels, col))
                if role in FIELDS and role not in block.columns:
                    block.columns[role] = col
        if "subject" not in block.columns:
            block.text_column = start
            if len(columns) > 1 and labels is not None:
                issues.append(Issue("столбцы", f"{group}: нет подписи «Дисциплина», пара читается из одного столбца",
                                    grid.where(header, start)))
        blocks.append(block)
    return blocks, issues
