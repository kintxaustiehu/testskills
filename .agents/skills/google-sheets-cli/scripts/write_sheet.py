#!/usr/bin/env python3
"""Write a value to a Google Sheets cell, or only change formatting."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Optional

import gspread


def _normalize_column_letter(column_letter: str) -> str:
    """Validate and normalize a spreadsheet column letter (A, I, AA, ...)."""
    normalized = column_letter.strip().upper()
    if not normalized or not re.fullmatch(r"[A-Z]+", normalized):
        raise ValueError(f"Invalid column letter: {column_letter!r}")
    return normalized


def write_cell_value(
    spreadsheet_id: str,
    column_letter: str,
    row_number: int,
    value: Optional[str],
    worksheet_name: Optional[str] = None,
) -> str:
    """Write to a target cell and return the A1-style cell address used."""
    if row_number < 1:
        raise ValueError("Row number must be >= 1")

    column = _normalize_column_letter(column_letter)
    cell_address = f"{column}{row_number}"

    client = gspread.service_account(filename="service-account.json")
    spreadsheet = client.open_by_key(spreadsheet_id)

    if worksheet_name is None:
        worksheet = spreadsheet.get_worksheet(0)
        if worksheet is None:
            raise ValueError("Spreadsheet has no worksheets")
    else:
        worksheet = spreadsheet.worksheet(worksheet_name)

    if value is not None:
        worksheet.update(range_name=cell_address, values=[[value]])
    else:
        worksheet.format(
            cell_address,
            {
                "backgroundColor": {
                    "red": 1.0,
                    "green": 0.95,
                    "blue": 0.6,
                }
            },
        )

    return cell_address


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a value to a Google Sheet cell, or only change cell background."
    )
    parser.add_argument(
        "--spreadsheet-id",
        required=True,
        help="Google Sheets spreadsheet ID",
    )
    parser.add_argument(
        "column",
        help="Column letter, for example A or I",
    )
    parser.add_argument(
        "row",
        type=int,
        help="1-indexed row number",
    )
    parser.add_argument(
        "value",
        nargs="?",
        default=None,
        help="Value to write (optional)",
    )
    parser.add_argument(
        "worksheet",
        nargs="?",
        default=None,
        help="Worksheet/tab name (optional, defaults to first sheet)",
    )

    args = parser.parse_args()

    try:
        cell_address = write_cell_value(
            spreadsheet_id=args.spreadsheet_id,
            column_letter=args.column,
            row_number=args.row,
            value=args.value,
            worksheet_name=args.worksheet,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Written to cell {cell_address}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
