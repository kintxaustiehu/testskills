#!/usr/bin/env python3
"""Read non-empty values from a specific Google Sheets column."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

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


def _rgb_to_hex(color: Dict[str, Any]) -> Optional[str]:
    if not color:
        return None

    red = color.get("red")
    green = color.get("green")
    blue = color.get("blue")
    if red is None or green is None or blue is None:
        return None

    try:
        r = int(round(red * 255))
        g = int(round(green * 255))
        b = int(round(blue * 255))
    except (TypeError, ValueError):
        return None

    return f"#{r:02x}{g:02x}{b:02x}"


def _background_color_from_cell(cell: Dict[str, Any]) -> Optional[str]:
    format_data = cell.get("effectiveFormat") or cell.get("userEnteredFormat")
    if not format_data:
        return None
    bg_color = format_data.get("backgroundColor")
    return _rgb_to_hex(bg_color) if isinstance(bg_color, dict) else None


def _find_sheet_meta(spreadsheet: Any, worksheet: Any) -> Dict[str, Any]:
    metadata = spreadsheet.fetch_sheet_metadata(includeGridData=True)
    worksheet_id = worksheet._properties.get("sheetId")
    for sheet in metadata.get("sheets", []):
        properties = sheet.get("properties", {})
        if properties.get("sheetId") == worksheet_id:
            return sheet
    raise ValueError("Worksheet metadata not found")


def get_column_values(
    spreadsheet_id: str,
    column_letter: str,
    worksheet_name: Optional[str] = None,
) -> List[Tuple[int, str, Optional[str]]]:
    """Return values from a column as (row_number, value, background_color) tuples."""
    client = gspread.service_account(filename="service-account.json")
    spreadsheet = client.open_by_key(spreadsheet_id)

    if worksheet_name is None:
        worksheet = spreadsheet.get_worksheet(0)
        if worksheet is None:
            raise ValueError("Spreadsheet has no worksheets")
    else:
        worksheet = spreadsheet.worksheet(worksheet_name)

    sheet_meta = _find_sheet_meta(spreadsheet, worksheet)
    grid_data = sheet_meta.get("data", [])
    row_data = grid_data[0].get("rowData", []) if grid_data else []

    col_idx = _column_letter_to_index(column_letter)
    results: List[Tuple[int, str, Optional[str]]] = []

    for row_number, row in enumerate(row_data, start=1):
        values = row.get("values", [])
        cell = values[col_idx - 1] if len(values) >= col_idx else {}
        value = cell.get("formattedValue") or ""
        background_color = _background_color_from_cell(cell)
        if value.strip() != "" or background_color is not None:
            results.append((row_number, value, background_color))

    return results


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
        payload = [
            {
                "row": row,
                "value": value,
                "background_color": background_color,
            }
            for row, value, background_color in rows
        ]
        print(json.dumps(payload, indent=2))
    else:
        for row, value, background_color in rows:
            rendered_value = value if value != "" else "(empty)"
            if background_color is not None:
                print(f"{row}: {rendered_value} [{background_color}]")
            else:
                print(f"{row}: {rendered_value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
