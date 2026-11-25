"""Генерирует три синтетических файла расписания в examples/input/.

Данные выдуманы. Каждый файл сделан «как в жизни»: свой формат и свой мусор.

    python examples/make_examples.py
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

OUT = Path(__file__).parent / "input"
THIN = Side(style="thin", color="999999")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD = PatternFill("solid", fgColor="FFF2CC")
WRAP = Alignment(wrap_text=True, vertical="center", horizontal="center")


def _put(ws, cell: str, value, merge_to: str | None = None, bold: bool = False, fill=None) -> None:
    ws[cell] = value
    if merge_to:
        ws.merge_cells(f"{cell}:{merge_to}")
    ws[cell].alignment = WRAP
    if bold:
        ws[cell].font = Font(bold=True)
    if fill:
        ws[cell].fill = fill


def _boxes(ws, cells: str) -> None:
    for row in ws[cells]:
        for cell in row:
            cell.border = BOX
            if cell.alignment is None or not cell.alignment.wrap_text:
                cell.alignment = WRAP


def _widths(ws, widths: dict[str, float]) -> None:
    for column, width in widths.items():
        ws.column_dimensions[column].width = width


def institute_a(path: Path) -> None:
    """Сетка с подписанными столбцами, поток на две группы, звёздочки, скрытый мусор."""
    book = Workbook()
    ws = book.active
    ws.title = "1 курс"
    _put(ws, "A1", "РАСПИСАНИЕ ЗАНЯТИЙ на осенний семестр 2026-2027 уч. года", "J1", bold=True)
    _put(ws, "A2", "Институт информационных технологий, 1 курс", "J2")
    _put(ws, "A3", "Дни недели", "A4", bold=True, fill=HEAD)
    _put(ws, "B3", "Время", "B4", bold=True, fill=HEAD)
    _put(ws, "C3", "Б-ИВТ-26 (25 чел.)", "F3", bold=True, fill=HEAD)
    _put(ws, "G3", "Б-ПМИ-26", "J3", bold=True, fill=HEAD)
    for col, label in zip("CDEF", ("Дисциплина", "Вид", "Преподаватель", "Ауд.")):
        _put(ws, f"{col}4", label, bold=True)
    for col, label in zip("GHIJ", ("Наименование дисциплины", "Вид занятия", "ФИО преподавателя", "Аудитория")):
        _put(ws, f"{col}4", label, bold=True)

    # Понедельник: строки 5-10, три пары по две строки (нечётная / чётная).
    _put(ws, "A5", "Понедельник", "A10")
    _put(ws, "B5", "8.00-9.35", "B6")
    _put(ws, "C5", "История России, лек., доц. Сидорова Е.В., ауд. 101", "J6")
    _put(ws, "B7", "9.50-11.25", "B8")
    for col, value in zip("CDEF", ("Математический анализ", "пр.", "Орлов А.Н.", 305)):
        _put(ws, f"{col}7", value, f"{col}8")
    for col, value in zip("GHIJ", ("Алгебра *", "лек", "Белова М.К.", 214)):
        _put(ws, f"{col}7", value)
    for col, value in zip("GHIJ", ("Геометрия **", "пр", "Белова М.К.", 214)):
        _put(ws, f"{col}8", value)
    _put(ws, "B9", "11:40 - 13:15", "B10")
    for col, value in zip("CDEF", ("Программирование", "лаб.", "ст. преп. Ким Д.С.", "412а")):
        _put(ws, f"{col}9", value, f"{col}10")

    # Вторник: строки 11-16, в середине скрытая строка с черновиком.
    _put(ws, "A11", "Вторник", "A16")
    _put(ws, "B11", "8.00-9.35", "B12")
    for col, value in zip("CDEF", ("Физика (н/н)", "лек", "Петров П.П.", 101)):
        _put(ws, f"{col}11", value)
    for col, value in zip("GHIJ", ("Дискретная математика", "лек", "Гусев В.В.", 210)):
        _put(ws, f"{col}11", value, f"{col}12")
    _put(ws, "C13", "ЧЕРНОВИК: перенести матан на пятницу?")
    ws.row_dimensions[13].hidden = True
    _put(ws, "B14", "9.50-11.25", "B15")
    for col, value in zip("CDEF", ("Английский язык", "пр", "Ли А.В.", "дист.")):
        _put(ws, f"{col}14", value, f"{col}15")
    for col, value in zip("GHIJ", ("Английский язык", "пр", "Ли А.В.", 330)):
        _put(ws, f"{col}14", value)
    for col, value in zip("GHIJ", ("Физическая культура", "пр", "Носов Т.Р.", "спортзал")):
        _put(ws, f"{col}15", value)

    # Среда: время с опечаткой, конец раньше начала.
    _put(ws, "A17", "Среда", "A18")
    _put(ws, "B17", "15.25-13.50", "B18")
    for col, value in zip("CDEF", ("Основы ИИ", "лек", "Орлов А.Н.", 101)):
        _put(ws, f"{col}17", value, f"{col}18")

    ws["K3"] = "заметки диспетчера"
    ws["K7"] = "уточнить аудиторию"
    ws.column_dimensions["K"].hidden = True
    _boxes(ws, "A3:J18")
    _widths(ws, {"A": 13, "B": 12, "C": 24, "D": 8, "E": 18, "F": 8, "G": 24, "H": 8, "I": 18, "J": 10})

    # Второй курс: другой порядок столбцов и сокращённые подписи.
    ws2 = book.create_sheet("2 курс")
    _put(ws2, "A1", "2 курс", "F1", bold=True)
    _put(ws2, "A2", "День", bold=True, fill=HEAD)
    _put(ws2, "B2", "Время", bold=True, fill=HEAD)
    _put(ws2, "C2", "Б-ИВТ-25", "F2", bold=True, fill=HEAD)
    for col, label in zip("CDEF", ("Дисциплина", "Ауд.", "Вид", "Преп.")):
        _put(ws2, f"{col}3", label, bold=True)
    lessons = (
        ("ПОНЕДЕЛЬНИК", "8.00-9.35", "Базы данных", 412, "лекция", "проф. Кузнецова Л.П."),
        ("", "9.50-11.25", "Базы данных", "412а", "лаб. раб.", "Кузнецова Л.П."),
        ("ЧЕТВЕРГ", "13.30-15.05", "Компьютерные сети", 214, "лек", "Гусев В.В."),
        ("", "15.20-16.55", "Компьютерные сети *", 214, "лаб", "Гусев В.В."),
    )
    for row, values in enumerate(lessons, start=4):
        for col, value in zip("ABCDEF", values):
            _put(ws2, f"{col}{row}", value)
    _boxes(ws2, "A2:F7")
    _widths(ws2, {"A": 14, "B": 12, "C": 24, "D": 8, "E": 10, "F": 22})

    old = book.create_sheet("Старое 2024")
    old["A1"] = "Б-ИВТ-24"
    old["A2"] = "Понедельник"
    old["B2"] = "8.00-9.35"
    old["C2"] = "Устаревший предмет"
    old.sheet_state = "hidden"
    book.save(path)


def institute_b(path: Path) -> None:
    """Одна ячейка на пару: всё записано текстом. Время только в первой строке пары."""
    book = Workbook()
    ws = book.active
    ws.title = "Магистратура"
    _put(ws, "D1", "УТВЕРЖДАЮ", bold=True)
    _put(ws, "D2", "Директор института ____________")
    _put(ws, "A4", "Расписание занятий магистратуры, 1 курс", "F4", bold=True)
    for col, label in zip("ABCDEF", ("День", "№", "Время", "М-ЭК-26", "М-ФН-26", "М-МН-26")):
        _put(ws, f"{col}6", label, bold=True, fill=HEAD)

    _put(ws, "A7", "ПН", "A10")
    rows = (
        (1, "08:00 - 09:35",
         "Микроэкономика (лек.) проф. Петров П.П. ауд. 412", "Микроэкономика (лек.) проф. Петров П.П. ауд. 412",
         "Теория менеджмента, лек., Белова М.К., 305"),
        ("", "",
         "", "", "(ч/н) Деловые коммуникации, пр., Ли А.В., 306"),
        (2, "9.50-11.25",
         "Эконометрика (пр.) Ким Д.С. 305 (н/н)", "Финансовые рынки, сем., доц. Орлов А.Н., ауд. 210",
         "Стратегический анализ (пр) Гусев В.В. дист."),
        ("", "",
         "Эконометрика (пр.) Ким Д.С. 305 (ч/н)", "", ""),
    )
    for row, values in enumerate(rows, start=7):
        for col, value in zip("BCDEF", values):
            _put(ws, f"{col}{row}", value)

    _put(ws, "A11", "ВТ", "A12")
    _put(ws, "B11", 1)
    _put(ws, "C11", "800-935")
    _put(ws, "D11", "Анализ данных, лаб, Кузнецова Л.П., 412а", "F11")
    _put(ws, "B12", 2)
    _put(ws, "C12", dt.time(9, 50))
    _put(ws, "E12", "Риск-менеджмент лек Сидорова Е.В. ауд.214")

    _boxes(ws, "A6:F12")
    _widths(ws, {"A": 6, "B": 4, "C": 14, "D": 34, "E": 34, "F": 34})
    book.save(path)


def college(path: Path) -> None:
    """Список из учётной системы: повторы шапки, пустые строки, итоги, разнобой в днях."""
    book = Workbook()
    ws = book.active
    ws.title = "Выгрузка"
    header = ("Группа", "День недели", "Время", "Дисциплина", "Вид", "Преподаватель", "Ауд.", "Неделя")
    ws.append(["Выгрузка расписания от 24.11.2026"])
    ws.append([])
    ws.append(header)
    data = (
        ("ПК-26", "пн.", "800-935", "Информатика", "лек", "Ким Д.С.", 101, ""),
        ("ПК-26", "", "9:50-11:25", "Математика", "пр", "Орлов А.Н.", 102, "нечет"),
        ("ПК-26", "", "9:50-11:25", "Русский язык", "пр", "Белова М.К.", 102, "чет"),
        (None, None, None, None, None, None, None, None),
        ("ПК-26, ПК-26-2", "Вт", "11.40-13.15", "Физкультура", "", "Носов Т.Р.", "спортзал", ""),
        header,
        ("СД-26", "СРЕДА", "8.00-9.35", "Анатомия", "лекция", "Петров П.П.", 205, ""),
        ("СД-26", "среда", "9.50-8.25", "Анатомия", "практ.", "Петров П.П.", 205, "1"),
        ("СД-26", "02.12.2026", "11.40-13.15", "Латинский язык", "пр", "Ли А.В.", 207, ""),
        ("СД-26", "завтра", "13.30-15.05", "Психология", "лек", "Сидорова Е.В.", 210, ""),
        ("Итого часов за неделю: 18",),
    )
    for values in data:
        ws.append([value for value in values if value is not None] if values[0] else [])
    for cell in ws[3]:
        cell.font = Font(bold=True)
    _widths(ws, {"A": 16, "B": 13, "C": 12, "D": 18, "E": 8, "F": 16, "G": 9, "H": 8})
    book.save(path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    institute_a(OUT / "institute_a.xlsx")
    institute_b(OUT / "institute_b.xlsx")
    college(OUT / "college.xlsx")
    print(f"Готово: {OUT}")


if __name__ == "__main__":
    main()
