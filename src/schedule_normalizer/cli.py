"""schedule-normalizer файлы... -o итог.xlsx"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import export
from .normalize import normalize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="schedule-normalizer",
        description="Сводит расписания из Excel-файлов разного вида в одну таблицу.",
    )
    parser.add_argument("files", nargs="+", type=Path, help="файлы .xlsx")
    parser.add_argument("-o", "--output", type=Path, default=Path("schedule.xlsx"),
                        help="куда сохранить: .xlsx, .csv или .json (по умолчанию schedule.xlsx)")
    parser.add_argument("-q", "--quiet", action="store_true", help="не печатать замечания")
    args = parser.parse_args(argv)

    missing = [str(path) for path in args.files if not path.is_file()]
    if missing:
        parser.error("нет таких файлов: " + ", ".join(missing))

    result = normalize(args.files)
    try:
        export.save(result, args.output)
    except ValueError as error:
        parser.error(str(error))

    print(f"Файлов: {len(args.files)}, листов: {result.sheets}, групп: {len(result.groups)}, "
          f"пар: {len(result.lessons)}, замечаний: {len(result.issues)}")
    if not args.quiet:
        for issue in result.issues:
            print(f"  [{issue.kind}] {issue.message}  ({issue.source})")
    print(f"Сохранено: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
