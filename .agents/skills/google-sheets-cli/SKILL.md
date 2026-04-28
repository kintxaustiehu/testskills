---
name: google-sheets-cli
description: Read from and write to Google Sheets using read_sheet.py and write_sheet.py. Use when asked to read column values, write cell values, or interact with Google Sheets programmatically.
---

## read_sheet.py

**Usage:** `python3 scripts/read_sheet.py --spreadsheet-id <SHEET_ID> <column> [worksheet] [--json]`

**Arguments:**
- `--spreadsheet-id` (required): Google Sheets ID
- `column` (required): Column letter (A, B, AA, etc.)
- `worksheet` (optional): Worksheet name (defaults to first sheet)
- `--json` (optional): Output JSON format

**Output (default):** `{row}: {value}` per line, filtered for non-empty cells

**Output (--json):** `[{"row": int, "value": string}, ...]`

## write_sheet.py

**Usage:** `python3 scripts/write_sheet.py --spreadsheet-id <SHEET_ID> <column> <row> [value] [worksheet]`

**Arguments:**
- `--spreadsheet-id` (required): Google Sheets ID
- `column` (required): Column letter (A, B, AA, etc.)
- `row` (required): 1-indexed row number
- `value` (optional): Value to write; omit for formatting-only mode
- `worksheet` (optional): Worksheet name (defaults to first sheet)

**Output:** `Written to cell {A1_address}.`

## Choosing Operations

**Read (read_sheet.py):** Extract values from a column
- Plain text: Display results, shell pipelines, logs
- JSON: Programmatic processing, structured data

**Write (write_sheet.py):** Update cells
- With value: Modify cell contents
- Without value: Apply background formatting only

## Setup

1. Place `service-account.json` in the same directory as the scripts
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure spreadsheet is shared with service account email from JSON

## Errors

- `FileNotFoundError: service-account.json` → Place credentials file in script directory
- `PermissionError` → Share spreadsheet with service account email
- `APIError [403]` → Enable Google Sheets API in service account project
- `APIError [429]` → Rate limited; retry after delay
