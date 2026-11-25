"""Лист Excel как прямоугольная сетка строк.

Объединённые ячейки раскрываются: значение копируется во все клетки
диапазона, а для каждой клетки запоминается её «исходная» ячейка. По ней
потом видно, что две строки или две группы делят одну запись.
Скрытые листы, строки и столбцы считаются пустыми: в них обычно черновики.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import column_index_from_string, get_column_letter

Cell = tuple[int, int]


def cell_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, dt.datetime):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, dt.time):
        return value.strftime("%H:%M")
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return " ".join(str(value).split())


@dataclass
class Grid:
    file: str
    sheet: str
    rows: list[list[str]]
    origins: dict[Cell, Cell] = field(default_factory=dict)

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return max((len(row) for row in self.rows), default=0)

    def value(self, row: int, col: int) -> str:
        if 0 <= row < self.height and 0 <= col < len(self.rows[row]):
            return self.rows[row][col]
        return ""

    def origin(self, row: int, col: int) -> Cell:
        return self.origins.get((row, col), (row, col))

    def row_is_empty(self, row: int) -> bool:
        return not any(self.rows[row])

    def where(self, row: int, col: int) -> str:
        origin_row, origin_col = self.origin(row, col)
        return f"{self.file} / {self.sheet} / {get_column_letter(origin_col + 1)}{origin_row + 1}"


def read_grids(path: str | Path) -> list[Grid]:
    """Все видимые листы книги."""
    path = Path(path)
    book = load_workbook(path, data_only=True)
    grids = []
    for sheet in book.worksheets:
        if sheet.sheet_state != "visible":
            continue
        rows = [
            [cell_text(cell.value) for cell in row]
            for row in sheet.iter_rows(max_row=sheet.max_row, max_col=sheet.max_column)
        ]
        origins: dict[Cell, Cell] = {}
        for merged in sheet.merged_cells.ranges:
            top, left = merged.min_row - 1, merged.min_col - 1
            value = rows[top][left]
            for row in range(top, merged.max_row):
                for col in range(left, merged.max_col):
                    rows[row][col] = value
                    origins[(row, col)] = (top, left)
        _blank_hidden(sheet, rows)
        grids.append(Grid(path.name, sheet.title, _trimmed(rows), origins))
    return grids


def _blank_hidden(sheet, rows: list[list[str]]) -> None:
    for index, dimension in sheet.row_dimensions.items():
        if dimension.hidden and 0 < index <= len(rows):
            rows[index - 1] = [""] * len(rows[index - 1])
    for letter, dimension in sheet.column_dimensions.items():
        if not dimension.hidden:
            continue
        first = dimension.min or column_index_from_string(letter)
        last = dimension.max or first
        for row in rows:
            for col in range(first - 1, min(last, len(row))):
                row[col] = ""


def _trimmed(rows: list[list[str]]) -> list[list[str]]:
    while rows and not any(rows[-1]):
        rows.pop()
    width = max((max((i + 1 for i, v in enumerate(row) if v), default=0) for row in rows), default=0)
    return [row[:width] for row in rows]
