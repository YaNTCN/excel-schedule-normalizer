"""Конвейер: файл -> листы -> раскладка листа -> пары -> проверки."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .grid import Grid, read_grids
from .layouts import list_table, week_grid
from .model import BOTH, Issue, Lesson, Result

# Список узнаётся по шапке и проверяется первым: в нём тоже есть дни и время.
LAYOUTS = (list_table, week_grid)


def normalize(paths: Iterable[str | Path]) -> Result:
    result = Result()
    for path in paths:
        result.extend(normalize_file(path))
    result.lessons.sort(key=Lesson.sort_key)
    result.issues.extend(overlaps(result.lessons))
    return result


def normalize_file(path: str | Path) -> Result:
    result = Result()
    for grid in read_grids(path):
        result.extend(normalize_grid(grid))
    return result


def normalize_grid(grid: Grid) -> Result:
    for layout_module in LAYOUTS:
        layout = layout_module.detect(grid)
        if layout is None:
            continue
        found = layout_module.extract(grid, layout)
        if found.lessons:
            return found
    if any(grid.rows):
        return Result(issues=[Issue("лист", "не нашёл на листе расписания", f"{grid.file} / {grid.sheet}")])
    return Result()


def overlaps(lessons: list[Lesson]) -> list[Issue]:
    """Две разные пары у одной группы в одно время одной недели."""
    by_slot: dict[tuple, list[Lesson]] = defaultdict(list)
    for lesson in lessons:
        if lesson.start:
            by_slot[(lesson.group, lesson.weekday, lesson.start)].append(lesson)

    issues = []
    for slot in by_slot.values():
        for index, first in enumerate(slot):
            for second in slot[index + 1:]:
                same_week = BOTH in (first.week, second.week) or first.week == second.week
                if not same_week or first.subject == second.subject:
                    continue
                hint = ""
                if first.week == second.week == BOTH:
                    hint = ", пометки недели нет: возможно, это разные недели"
                issues.append(Issue(
                    "накладка",
                    f"{first.group}, {first.weekday_name} {first.start}: "
                    f"«{first.subject}» и «{second.subject}» в одно время{hint}",
                    first.source,
                ))
    return issues
