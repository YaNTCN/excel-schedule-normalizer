import pytest

from schedule_normalizer import cells, times, vocab
from schedule_normalizer.model import BOTH, EVEN, ODD


@pytest.mark.parametrize("text, expected", [
    ("8.00-9.35", ("08:00", "09:35")),
    ("08:00 – 09:35", ("08:00", "09:35")),
    ("с 8:00 до 9:35", ("08:00", "09:35")),
    ("1 пара 8.00-9.35", ("08:00", "09:35")),
    ("800-935", ("08:00", "09:35")),
    ("09:50", ("09:50", None)),
    ("25.00-26.00", None),
    ("Б-ИВТ-26", None),
    ("", None),
])
def test_parse_time(text, expected):
    assert times.parse_time(text) == expected


def test_reversed_time():
    assert times.is_reversed(("15:25", "13:50"))
    assert not times.is_reversed(("08:00", "09:35"))
    assert not times.is_reversed(("08:00", None))


@pytest.mark.parametrize("text, day", [
    ("Понедельник", 1), ("ПН", 1), ("пн.", 1), ("понед", 1),
    ("СРЕДА", 3), ("Сб", 6), ("02.12.2026", 3),
    ("завтра", None), ("31.02.2026", None), ("", None),
])
def test_weekday(text, day):
    assert vocab.weekday(text) == day


@pytest.mark.parametrize("text, groups", [
    ("Б-ИВТ-26 (25 чел.)", ["Б-ИВТ-26"]),
    ("ПК-26, ПК-26-2", ["ПК-26", "ПК-26-2"]),
    ("м-эк-26", ["М-ЭК-26"]),
    ("ауд. КФ-536", []),
    ("Итого часов за неделю: 18", []),
])
def test_groups_in(text, groups):
    assert vocab.groups_in(text) == groups


@pytest.mark.parametrize("text, kind", [
    ("лек", "лекция"), ("Лекция", "лекция"), ("пр.", "практика"), ("практ.", "практика"),
    ("лаб. раб.", "лабораторная"), ("л/р", "лабораторная"), ("сем", "семинар"), ("зачёт", "зачёт"),
])
def test_lesson_type(text, kind):
    assert vocab.lesson_type(text) == kind


@pytest.mark.parametrize("text, expected", [
    ("Алгебра *", ("Алгебра", ODD)),
    ("Геометрия **", ("Геометрия", EVEN)),
    ("Физика (н/н)", ("Физика", ODD)),
    ("(ч/н) Деловые коммуникации", ("Деловые коммуникации", EVEN)),
    ("Математика", ("Математика", BOTH)),
    ("Учёт и аудит", ("Учёт и аудит", BOTH)),
])
def test_split_week(text, expected):
    assert cells.split_week(text) == expected


@pytest.mark.parametrize("value, week", [("нечет", ODD), ("чёт", EVEN), ("1", ODD), ("II", EVEN), ("", BOTH)])
def test_week_value(value, week):
    assert cells.week_value(value) == week


@pytest.mark.parametrize("text, expected", [
    ("Микроэкономика (лек.) проф. Петров П.П. ауд. 412",
     cells.Parsed("Микроэкономика", "лекция", "Петров П.П.", "412")),
    ("История России, лек., доц. Сидорова Е.В., ауд. 101",
     cells.Parsed("История России", "лекция", "Сидорова Е.В.", "101")),
    ("Стратегический анализ (пр) Гусев В.В. дист.",
     cells.Parsed("Стратегический анализ", "практика", "Гусев В.В.", "онлайн")),
    ("Риск-менеджмент лек Сидорова Е.В. ауд.214",
     cells.Parsed("Риск-менеджмент", "лекция", "Сидорова Е.В.", "214")),
    ("Анализ данных, лаб, Кузнецова Л.П., 412а",
     cells.Parsed("Анализ данных", "лабораторная", "Кузнецова Л.П.", "412а")),
    ("Кабельные сети, пр, Ли А. В.",
     cells.Parsed("Кабельные сети", "практика", "Ли А.В.", "")),
    ("Практикум по программированию",
     cells.Parsed("Практикум по программированию")),
])
def test_parse_lesson(text, expected):
    assert cells.parse_lesson(text) == expected


def test_teacher_and_room_columns():
    assert cells.teacher_name("ст. преп. Ким Д.С.") == "Ким Д.С."
    assert cells.teacher_name("Иванов И.И., Петров П.П.") == "Иванов И.И., Петров П.П."
    assert cells.teacher_name("вакансия") == "вакансия"
    assert cells.room_name("ауд. 412") == "412"
    assert cells.room_name("дист.") == "онлайн"
    assert cells.room_name("спортзал") == "спортзал"
