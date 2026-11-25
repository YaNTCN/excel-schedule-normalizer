"""Время пары в том виде, в каком его пишут в таблицах.

Встречается «8.00-9.35», «08:00 – 09:35», «с 8:00 до 9:35», «800-935»,
время ячейкой Excel («08:00») и время с припиской «1 пара 8.00-9.35».
"""

from __future__ import annotations

import re

_HM = r"(\d{1,2})[.:](\d{2})"
_DASH = r"\s*(?:-|–|—|до)\s*"
RANGE_RE = re.compile(_HM + _DASH + _HM)
COMPACT_RE = re.compile(r"^(\d{3,4})\s*[-–—]\s*(\d{3,4})$")
SINGLE_RE = re.compile(r"^(?:с\s*)?" + _HM + r"$")

TimeRange = tuple[str, str | None]


def _hm(hours: str, minutes: str) -> str | None:
    h, m = int(hours), int(minutes)
    if h > 23 or m > 59:
        return None
    return f"{h:02d}:{m:02d}"


def parse_time(text: str) -> TimeRange | None:
    """(начало, конец) или None, если в ячейке не время. Конца может не быть."""
    text = text.strip().lower()
    if not text:
        return None
    if match := RANGE_RE.search(text):
        start, end = _hm(*match.group(1, 2)), _hm(*match.group(3, 4))
        return (start, end) if start and end else None
    if match := COMPACT_RE.match(text):
        a, b = match.groups()
        start, end = _hm(a[:-2], a[-2:]), _hm(b[:-2], b[-2:])
        return (start, end) if start and end else None
    if match := SINGLE_RE.match(text):
        start = _hm(*match.groups())
        return (start, None) if start else None
    return None


def is_time(text: str) -> bool:
    return parse_time(text) is not None


def is_reversed(time: TimeRange) -> bool:
    start, end = time
    return end is not None and end <= start
