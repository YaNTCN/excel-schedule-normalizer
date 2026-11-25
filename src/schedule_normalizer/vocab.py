"""Слова, по которым узнаются дни недели, группы, виды занятий и шапки столбцов."""

from __future__ import annotations

import datetime as dt
import re

_WEEKDAYS = {
    "пн": 1, "понедельник": 1,
    "вт": 2, "вторник": 2,
    "ср": 3, "среда": 3,
    "чт": 4, "четверг": 4,
    "пт": 5, "пятница": 5,
    "сб": 6, "суббота": 6,
    "вс": 7, "воскресенье": 7,
}
_FULL_NAMES = {name: day for name, day in _WEEKDAYS.items() if len(name) > 2}
_DATE_RE = re.compile(r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$")

# Б-ИВТ-26, М-ЭК-26, ПК-26, Б-ИВТ-26-2: уровень, направление, год набора, подгруппа.
GROUP_RE = re.compile(r"(?<![А-ЯЁA-Z\w-])(?:[А-ЯЁA-Z]{1,2}-)?[А-ЯЁA-Z]{2,6}-\d{2}(?:-\d{1,2})?(?![\w-])")

_TYPES = (
    (re.compile(r"(?<![а-яё])лек(?:ция|ц)?\.?(?![а-яё])", re.I), "лекция"),
    (re.compile(r"(?<![а-яё])(?:практ(?:ика)?|пр)\.?(?![а-яё])", re.I), "практика"),
    (re.compile(r"(?<![а-яё])(?:лаб(?:\.\s*раб(?:ота)?|ораторная(?:\s+работа)?)?|л/р|лр)\.?(?![а-яё])", re.I), "лабораторная"),
    (re.compile(r"(?<![а-яё])сем(?:инар)?\.?(?![а-яё])", re.I), "семинар"),
)

COLUMN_ROLES = {
    "group": ("групп",),
    "weekday": ("день", "дни", "дата"),
    "time": ("время",),
    "start": ("начало",),
    "end": ("оконч", "конец"),
    "week": ("недел",),
    "subject": ("дисципл", "предмет", "наименован"),
    "type": ("вид", "тип"),
    "teacher": ("преп", "фио"),
    "room": ("ауд", "каб"),
}


def weekday(text: str) -> int | None:
    """1..7 по названию дня («Пн», «пн.», «ПОНЕДЕЛЬНИК», «понед») или по дате."""
    word = text.strip().lower().rstrip(".")
    if not word:
        return None
    if word in _WEEKDAYS:
        return _WEEKDAYS[word]
    if len(word) >= 4:
        for name, day in _FULL_NAMES.items():
            if name.startswith(word):
                return day
    if match := _DATE_RE.match(word):
        day, month, year = (int(part) for part in match.groups())
        try:
            return dt.date(year, month, day).isoweekday()
        except ValueError:
            return None
    return None


def groups_in(text: str) -> list[str]:
    return GROUP_RE.findall(text.upper())


def lesson_type(text: str) -> str:
    """Вид занятия в едином написании; незнакомое слово остаётся как есть."""
    for pattern, name in _TYPES:
        if pattern.fullmatch(text.strip()):
            return name
    return text.strip()


def find_type(text: str) -> tuple[str, str]:
    """Ищет вид занятия внутри текста: (вид, текст без него)."""
    for pattern, name in _TYPES:
        if match := pattern.search(text):
            return name, text[: match.start()] + " " + text[match.end():]
    return "", text


def column_role(label: str) -> str | None:
    label = label.lower()
    for role, words in COLUMN_ROLES.items():
        if any(word in label for word in words):
            return role
    return None
