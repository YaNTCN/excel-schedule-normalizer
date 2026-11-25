"""Итоговая модель: одна пара одной группы и замечание к исходному файлу."""

from __future__ import annotations

from dataclasses import dataclass, field

WEEKDAY_NAMES = (
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
)

ODD, EVEN, BOTH = "odd", "even", "both"
WEEK_NAMES = {ODD: "нечётная", EVEN: "чётная", BOTH: "каждая"}
_WEEK_ORDER = {BOTH: 0, ODD: 1, EVEN: 2}


@dataclass(frozen=True)
class Lesson:
    group: str
    weekday: int
    start: str | None
    end: str | None
    subject: str
    type: str = ""
    teacher: str = ""
    room: str = ""
    week: str = BOTH
    source: str = ""

    @property
    def weekday_name(self) -> str:
        return WEEKDAY_NAMES[self.weekday - 1]

    def sort_key(self) -> tuple:
        return (self.group, self.weekday, self.start or "99:99", _WEEK_ORDER[self.week], self.subject)


@dataclass(frozen=True)
class Issue:
    kind: str
    message: str
    source: str = ""


@dataclass
class Result:
    lessons: list[Lesson] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)
    sheets: int = 0

    def extend(self, other: Result) -> None:
        self.lessons.extend(other.lessons)
        self.issues.extend(other.issues)
        self.sheets += other.sheets

    @property
    def groups(self) -> list[str]:
        return sorted({lesson.group for lesson in self.lessons})
