#!/usr/bin/env python3
"""Read non-empty values from a specific Google Sheets column."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import List, Optional, Tuple

import gspread


def _column_letter_to_index(column_letter: str) -> int:
    """Convert a spreadsheet column letter (for example A, I, AA) to a 1-based index."""
    normalized = column_letter.strip().upper()
    if not normalized or not re.fullmatch(r"[A-Z]+", normalized):
        raise ValueError(f"Invalid column letter: {column_letter!r}")

    index = 0
    for char in normalized:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index


def get_column_values(
    spreadsheet_id: str,
    column_letter: str,
    worksheet_name: Optional[str] = None,
) -> List[Tuple[int, str]]:
    """Return non-empty values from a column as (row_number, value) tuples."""
    client = gspread.service_account(filename="service-account.json")
    spreadsheet = client.open_by_key(spreadsheet_id)

    if worksheet_name is None:
        worksheet = spreadsheet.get_worksheet(0)
        if worksheet is None:
            raise ValueError("Spreadsheet has no worksheets")
    else:
        worksheet = spreadsheet.worksheet(worksheet_name)

    col_idx = _column_letter_to_index(column_letter)
    values = worksheet.col_values(col_idx)

    return [
        (row_number, value)
        for row_number, value in enumerate(values, start=1)
        if value.strip() != ""
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read non-empty values from a Google Sheet column."
    )
    parser.add_argument(
        "--spreadsheet-id",
        required=True,
        help="Google Sheets spreadsheet ID",
    )
    parser.add_argument(
        "column",
        help="Column letter to read, for example A or I",
    )
    parser.add_argument(
        "worksheet",
        nargs="?",
        default=None,
        help="Worksheet/tab name (optional, defaults to the first sheet)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output JSON instead of plain text",
    )

    args = parser.parse_args()

    try:
        rows = get_column_values(
            spreadsheet_id=args.spreadsheet_id,
            column_letter=args.column,
            worksheet_name=args.worksheet,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        payload = [{"row": row, "value": value} for row, value in rows]
        print(json.dumps(payload, indent=2))
    else:
        for row, value in rows:
            print(f"{row}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
