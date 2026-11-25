"""Разбор содержимого ячеек: пометки недели и пара, записанная одной строкой."""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import vocab
from .model import BOTH, EVEN, ODD

# Сначала нечётная: «нечёт» содержит «чёт».
_ODD_RE = re.compile(r"\(?(?<![а-яё])(?:н/н|неч(?:[её]т(?:н[а-яё]*)?)?\.?)(?![а-яё])\)?", re.I)
_EVEN_RE = re.compile(r"\(?(?<![а-яё])(?:ч/н|ч[её]т(?:н[а-яё]*)?\.?)(?![а-яё])\)?", re.I)
_STARS_RE = re.compile(r"(?<!\*)(\*{1,2})(?!\*)")

_TITLE = r"(?i:проф|доц|ст\.?\s*преп|преп|асс)\.?\s*"
_TEACHER_RE = re.compile(
    rf"(?:{_TITLE})?([А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?\s+[А-ЯЁ]\.\s*(?:[А-ЯЁ]\.)?)"
)
_TITLE_RE = re.compile(rf"^{_TITLE}", re.I)
_ROOM_RE = re.compile(r"(?:ауд(?:итория)?|каб(?:инет)?)(?![а-яё])\.?\s*([\w/-]+)", re.I)
_ROOM_TAIL_RE = re.compile(r"(?<![\w.])(\d{3,4}[а-яa-z]?)\s*$", re.I)
_ONLINE_RE = re.compile(r"(?<![а-яё])(?:дист\w*\.?|онлайн|zoom|online)", re.I)
_EDGES = " ,;:-–—/()."


def split_week(text: str) -> tuple[str, str]:
    """Убирает пометку недели из текста: (текст, odd | even | both).

    «*» и «н/н» значат нечётную неделю, «**» и «ч/н» чётную.
    """
    for pattern, week in ((_ODD_RE, ODD), (_EVEN_RE, EVEN)):
        if pattern.search(text):
            return _tidy(pattern.sub(" ", text, count=1)), week
    if match := _STARS_RE.search(text):
        week = ODD if len(match.group(1)) == 1 else EVEN
        return _tidy(text[: match.start()] + " " + text[match.end():]), week
    return text, BOTH


def week_value(text: str) -> str:
    """Неделя из отдельного столбца: «нечёт», «ч/н», «*», «1», «2»."""
    value = text.strip().lower()
    if value in {"1", "i"}:
        return ODD
    if value in {"2", "ii"}:
        return EVEN
    return split_week(value)[1]


def room_name(text: str) -> str:
    """Аудитория из отдельного столбца: «ауд. 412» -> «412», «дист.» -> «онлайн»."""
    if _ONLINE_RE.fullmatch(text.strip()):
        return "онлайн"
    if match := _ROOM_RE.fullmatch(text.strip()):
        return match.group(1)
    return text.strip()


def teacher_name(text: str) -> str:
    """Преподаватель без должности: «доц. Петров П.П.» -> «Петров П.П.»."""
    names = [_initials(name) for name in _TEACHER_RE.findall(text)]
    return ", ".join(names) if names else _tidy(_TITLE_RE.sub("", text))


@dataclass(frozen=True)
class Parsed:
    subject: str
    type: str = ""
    teacher: str = ""
    room: str = ""


def parse_lesson(text: str) -> Parsed:
    """Пара, записанная в одну ячейку.

    «Микроэкономика (лек.) проф. Петров П.П. ауд. 412»
    «История России, лек., доц. Сидорова Е.В., 101»
    """
    rest = text
    teachers = [_initials(name) for name in _TEACHER_RE.findall(rest)]
    rest = _TEACHER_RE.sub(" ", rest)

    room = ""
    if match := _ROOM_RE.search(rest):
        room = match.group(1)
        rest = rest[: match.start()] + " " + rest[match.end():]
    elif match := _ONLINE_RE.search(rest):
        room = "онлайн"
        rest = rest[: match.start()] + " " + rest[match.end():]
    elif match := _ROOM_TAIL_RE.search(_tidy(rest)):
        room = match.group(1)
        rest = _tidy(rest)[: match.start()]

    kind, rest = vocab.find_type(rest)
    return Parsed(_tidy(rest), kind, ", ".join(teachers), room)


def _initials(name: str) -> str:
    return re.sub(r"\.\s+", ".", " ".join(name.split()))


def _tidy(text: str) -> str:
    text = re.sub(r"\(\s*\)", " ", text)
    text = re.sub(r"\s*,\s*(?:,\s*)+", ", ", text)
    return " ".join(text.split()).strip(_EDGES)
