---
name: google-sheets-cli
description: Read from and write to Google Sheets using read_sheet.py and write_sheet.py. Use when asked to read column values, write cell values, or interact with Google Sheets programmatically.
---

# Google Sheets CLI Skill

This skill provides two command-line tools for reading and writing values in Google Sheets:
- `read_sheet.py`: Read non-empty values from a column
- `write_sheet.py`: Write values to specific cells

## Prerequisites

Before using this skill, ensure:

1. A Google service account is set up with access to the target spreadsheet
2. The service account credentials file is saved as `service-account.json` in the project root
3. The gspread Python library is installed: `pip install gspread`
4. The spreadsheet is shared with the service account email address

## read_sheet.py - Reading Column Values

### Usage

```bash
python3 read_sheet.py --spreadsheet-id <SHEET_ID> <column> [worksheet] [--json]
```

### Arguments

- `--spreadsheet-id` (required): The Google Sheets ID (from the URL)
- `column` (required, positional): Column letter (A, B, AA, etc.)
- `worksheet` (optional, positional): Worksheet/tab name (defaults to first sheet)
- `--json` (optional flag): Output as JSON instead of plain text

### Output Format

**Default (plain text):**
```
1: Header Value
3: Row 3 Value
5: Row 5 Value
```

**With --json flag:**
```json
[
  {"row": 1, "value": "Header Value"},
  {"row": 3, "value": "Row 3 Value"},
  {"row": 5, "value": "Row 5 Value"}
]
```

### Examples

Read column A from the first worksheet:
```bash
python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A
```

Read column I from a specific worksheet:
```bash
python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI I "Sheet1"
```

Read as JSON:
```bash
python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A --json
```

## write_sheet.py - Writing Cell Values

### Usage

```bash
python3 write_sheet.py --spreadsheet-id <SHEET_ID> <column> <row> [value] [worksheet]
```

### Arguments

- `--spreadsheet-id` (required): The Google Sheets ID
- `column` (required, positional): Column letter (A, B, AA, etc.)
- `row` (required, positional): 1-indexed row number
- `value` (optional, positional): Value to write; if omitted, only changes cell background formatting
- `worksheet` (optional, positional): Worksheet/tab name (defaults to first sheet)

### Output

```
Written to cell A6.
```

### Examples

Write a value to cell A6:
```bash
python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A 6 "studentA6"
```

Write to a specific worksheet:
```bash
python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI B 10 "New Value" "Sheet2"
```

Format a cell without changing its value (highlighting only):
```bash
python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI C 5
```

## Key Features

### read_sheet.py
- Filters empty cells automatically
- Returns 1-indexed row numbers for compatibility with spreadsheet UI
- Supports both plain text and JSON output
- Optional worksheet/tab selection
- Uses gspread's `col_values()` for efficient column reads

### write_sheet.py
- Writes to any cell in a 1-indexed coordinate system
- Returns the A1-style cell address for confirmation
- Supports formatting-only mode (changes background without overwriting value)
- Optional worksheet/tab selection
- Uses gspread's `update()` method for cell writes

## Integration with Agent Workflows

When an agent uses this skill, it should:

1. **For reading data**: Use `read_sheet.py` to fetch values from a column, optionally filtering with `--json` for structured data
2. **For writing data**: Use `write_sheet.py` to update cells, with the row/column/value as positional arguments
3. **For verification**: Combine both tools to verify writes by reading back the data

## Troubleshooting

- **PermissionError**: Ensure the spreadsheet is shared with the service account email
- **APIError [403]**: Enable Google Sheets API in the service account project
- **FileNotFoundError**: Ensure `service-account.json` is in the project root directory

## See Also

- Full documentation: See `references/usage-guide.md` for detailed examples
- Demo document: See `demo.md` in the project root for real-world examples
- Verification: Run `tests/proof_verify_mock.py` for offline verification
