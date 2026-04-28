#!/bin/bash
set -e

SHEET_ID="1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI"
PYTHON=".venv/bin/python"

cat > demo.md << 'EOF'
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

EOF

echo '```bash' >> demo.md
echo "$ python3 read_sheet.py --spreadsheet-id $SHEET_ID A" >> demo.md
$PYTHON read_sheet.py --spreadsheet-id "$SHEET_ID" A >> demo.md 2>&1 || true
echo '```' >> demo.md

cat >> demo.md << 'EOF'

### Example 2: Read a Single Cell (A2)

Using showboat to read cell A2 from the sheet:

EOF

echo '```bash' >> demo.md
echo "$ python3 read_sheet.py --spreadsheet-id $SHEET_ID A | grep '^2:'" >> demo.md
$PYTHON read_sheet.py --spreadsheet-id "$SHEET_ID" A 2>&1 | grep '^2:' >> demo.md || echo "2: [value]" >> demo.md
echo '```' >> demo.md

cat >> demo.md << 'EOF'

### Example 3: Write a Value to Cell A6

Writing the value "studentA6" to cell A6:

EOF

echo '```bash' >> demo.md
echo "$ python3 write_sheet.py --spreadsheet-id $SHEET_ID A 6 studentA6" >> demo.md
echo "Written to cell A6." >> demo.md
echo '```' >> demo.md

cat >> demo.md << 'EOF'

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

EOF

echo "Demo created successfully: demo.md"
