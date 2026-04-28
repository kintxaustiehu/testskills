# Google Sheets CLI Tools Demo

This document demonstrates the features of `read_sheet.py` and `write_sheet.py`, two Python CLI tools for reading and writing values in Google Sheets.

## Features

### read_sheet.py

- Read non-empty values from a Google Sheets column
- Return results as (row_number, value) tuples with 1-indexed rows
- Support optional worksheet/tab selection
- Output in plain text or JSON format
- Filter empty cells automatically

### write_sheet.py

- Write values to specific cells in Google Sheets
- Return the A1-style cell address of the target cell
- Optional value parameter for formatting-only mode
- Support optional worksheet/tab selection
- Automatic cell background formatting when value is omitted

## Examples

### Example 1: Read Column A Values

Reading all non-empty values from column A:

```bash
$ python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A
1: Email
2: mleon019@ikasle.ehu.eus
3: kintxausti001@ikasle.ehu.eus
4: precaj001@ikasle.ehu.eus
5: juanan.pereira@ehu.eus
```

### Example 2: Read a Single Cell (A2)

Using showboat to read cell A2 from the sheet:

```bash
$ python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A | grep '^2:'
2: mleon019@ikasle.ehu.eus
```

### Example 3: Write a Value to Cell A6

Writing the value "studentA6" to cell A6:

```bash
$ python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A 6 studentA6
Written to cell A6.
```

## JSON Output Format

The read_sheet tool also supports JSON output:

```bash
$ python3 read_sheet.py --spreadsheet-id YOUR_SHEET_ID A --json
[
  {
    "row": 1,
    "value": "Column A Header"
  },
  {
    "row": 3,
    "value": "Another Value"
  }
]
```

## Command-Line Arguments

### read_sheet.py

- `--spreadsheet-id` (required): Google Sheet ID
- `column` (required, positional): Column letter (e.g., A, I, AA)
- `worksheet` (optional, positional): Worksheet/tab name
- `--json` (optional flag): Output as JSON

### write_sheet.py

- `--spreadsheet-id` (required): Google Sheet ID
- `column` (required, positional): Column letter
- `row` (required, positional): 1-indexed row number
- `value` (optional, positional): Value to write
- `worksheet` (optional, positional): Worksheet/tab name

