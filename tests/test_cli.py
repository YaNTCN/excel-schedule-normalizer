import json
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

from schedule_normalizer.cli import main

INPUT = Path(__file__).parent.parent / "examples" / "input"


def test_xlsx_output(tmp_path, capsys):
    out = tmp_path / "schedule.xlsx"
    assert main([str(INPUT / "college.xlsx"), "-o", str(out)]) == 0
    book = load_workbook(out)
    assert book.sheetnames == ["Расписание", "Замечания"]
    assert book["Расписание"]["A1"].value == "Группа"
    assert "пар: 8" in capsys.readouterr().out


def test_json_output(tmp_path):
    out = tmp_path / "schedule.json"
    main([str(INPUT / "institute_b.xlsx"), "-o", str(out), "-q"])
    data = json.loads(out.read_text(encoding="utf-8"))
    assert {lesson["group"] for lesson in data["lessons"]} == {"М-ЭК-26", "М-ФН-26", "М-МН-26"}


def test_unknown_sheet_is_reported(tmp_path, capsys):
    path = tmp_path / "notes.xlsx"
    book = Workbook()
    book.active["A1"] = "Просто заметки"
    book.save(path)
    main([str(path), "-o", str(tmp_path / "out.csv")])
    assert "не нашёл на листе расписания" in capsys.readouterr().out


def test_missing_file_and_bad_format(tmp_path):
    with pytest.raises(SystemExit):
        main([str(tmp_path / "nope.xlsx")])
    with pytest.raises(SystemExit):
        main([str(INPUT / "college.xlsx"), "-o", str(tmp_path / "out.txt")])
