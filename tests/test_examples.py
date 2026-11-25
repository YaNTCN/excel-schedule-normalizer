"""Сквозная проверка на трёх синтетических файлах из examples/input."""

from pathlib import Path

import pytest

from schedule_normalizer import normalize
from schedule_normalizer.model import BOTH, EVEN, ODD

INPUT = Path(__file__).parent.parent / "examples" / "input"


@pytest.fixture(scope="module")
def result():
    return normalize(sorted(INPUT.glob("*.xlsx")))


def find(result, group, weekday, start):
    return [lesson for lesson in result.lessons
            if lesson.group == group and lesson.weekday == weekday and lesson.start == start]


def kinds(result):
    return sorted(issue.kind for issue in result.issues)


def test_summary(result):
    assert result.sheets == 4
    assert result.groups == ["Б-ИВТ-25", "Б-ИВТ-26", "Б-ПМИ-26", "М-МН-26", "М-ФН-26",
                             "М-ЭК-26", "ПК-26", "ПК-26-2", "СД-26"]
    assert len(result.lessons) == 36
    assert kinds(result) == ["время", "время", "день", "накладка", "накладка"]


def test_stream_lecture_goes_to_both_groups(result):
    for group in ("Б-ИВТ-26", "Б-ПМИ-26"):
        [lesson] = find(result, group, 1, "08:00")
        assert (lesson.subject, lesson.type, lesson.teacher, lesson.room) == (
            "История России", "лекция", "Сидорова Е.В.", "101")


def test_vertical_merge_is_one_lesson_for_both_weeks(result):
    [lesson] = find(result, "Б-ИВТ-26", 1, "09:50")
    assert lesson.subject == "Математический анализ"
    assert lesson.week == BOTH


def test_stars_split_weeks(result):
    lessons = find(result, "Б-ПМИ-26", 1, "09:50")
    assert [(lesson.subject, lesson.week) for lesson in lessons] == [("Алгебра", ODD), ("Геометрия", EVEN)]


def test_hidden_rows_columns_and_sheets_are_ignored(result):
    assert not any("ЧЕРНОВИК" in lesson.subject for lesson in result.lessons)
    assert "Б-ИВТ-24" not in result.groups


def test_columns_in_other_order(result):
    [lesson] = find(result, "Б-ИВТ-25", 1, "09:50")
    assert (lesson.subject, lesson.type, lesson.teacher, lesson.room) == (
        "Базы данных", "лабораторная", "Кузнецова Л.П.", "412а")


def test_text_cells_and_time_only_on_first_row(result):
    lessons = find(result, "М-ЭК-26", 1, "09:50")
    assert [(lesson.subject, lesson.week, lesson.end) for lesson in lessons] == [
        ("Эконометрика", ODD, "11:25"), ("Эконометрика", EVEN, "11:25")]


def test_excel_time_cell_without_end(result):
    [lesson] = find(result, "М-ФН-26", 2, "09:50")
    assert (lesson.subject, lesson.end) == ("Риск-менеджмент", None)


def test_list_table(result):
    [lesson] = find(result, "СД-26", 3, "11:40")
    assert lesson.subject == "Латинский язык"
    assert {lesson.group for lesson in result.lessons if lesson.subject == "Физкультура"} == {"ПК-26", "ПК-26-2"}
    assert [lesson.week for lesson in find(result, "ПК-26", 1, "09:50")] == [ODD, EVEN]


def test_every_lesson_knows_its_cell(result):
    [lesson] = find(result, "М-ФН-26", 1, "08:00")
    assert lesson.source == "institute_b.xlsx / Магистратура / E7"
