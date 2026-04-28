# Google Sheets CLI - Complete Usage Guide

This guide provides detailed examples and best practices for using `read_sheet.py` and `write_sheet.py`.

## Getting Started

### 1. Verify Prerequisites

Before using the scripts, ensure:

```bash
# Check that service-account.json exists
ls service-account.json

# Verify gspread is installed
python3 -c "import gspread; print(f'gspread version: {gspread.__version__}')"

# Test a simple read
python3 read_sheet.py --spreadsheet-id YOUR_SHEET_ID A
```

### 2. Activate Virtual Environment (if using one)

```bash
source .venv/bin/activate
```

## Common Use Cases

### Use Case 1: Reading a Roster from a Column

**Scenario**: You have a spreadsheet with student names in column A.

```bash
python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A
```

**Output**:
```
1: Students
2: Alice
3: Bob
4: Charlie
```

### Use Case 2: Reading Email Addresses and Processing with JSON

**Scenario**: Extract emails from column B and process them programmatically.

```bash
python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI B --json
```

**Output**:
```json
[
  {"row": 1, "value": "Email"},
  {"row": 2, "value": "alice@example.com"},
  {"row": 3, "value": "bob@example.com"}
]
```

### Use Case 3: Writing Grades to a Spreadsheet

**Scenario**: Update student grades in column C based on test results.

```bash
# Write grade for student in row 2
python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI C 2 "A"

# Write grade for student in row 3
python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI C 3 "B+"
```

### Use Case 4: Highlighting Cells Without Changing Values

**Scenario**: Mark cells for review by changing their background color.

```bash
# Highlight cell D5 without modifying its value
python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI D 5
```

This applies a light yellow background to the cell without overwriting its contents.

### Use Case 5: Working with Multiple Worksheets

**Scenario**: Your spreadsheet has multiple sheets (e.g., "Students" and "Grades").

```bash
# Read from the Students sheet
python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A "Students"

# Write to the Grades sheet
python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI B 10 "A+" "Grades"
```

## Advanced Patterns

### Batch Processing with Shell Scripts

**Read all rows and process each one:**

```bash
python3 read_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI A | while read line; do
  row=$(echo "$line" | cut -d: -f1)
  value=$(echo "$line" | cut -d: -f2 | xargs)
  echo "Processing row $row: $value"
done
```

### JSON Processing with Python

**Parse JSON output and perform calculations:**

```python
import subprocess
import json

result = subprocess.run([
    'python3', 'read_sheet.py',
    '--spreadsheet-id', '1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI',
    'A', '--json'
], capture_output=True, text=True)

data = json.loads(result.stdout)
for item in data:
    print(f"Row {item['row']}: {item['value']}")
```

### Conditional Writes

**Write based on conditions:**

```bash
# Write "PASS" to B2 if a condition is met
if [ some_condition ]; then
    python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI B 2 "PASS"
else
    python3 write_sheet.py --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI B 2 "FAIL"
fi
```

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: service-account.json` | Credentials file missing | Place service account JSON in project root |
| `PermissionError: [403]` | API not enabled or sheet not shared | Enable Sheets API and share sheet with service account email |
| `APIError: [429]` | Rate limit exceeded | Wait 60-90 seconds before retrying |
| `ValueError: Invalid column letter` | Wrong column format | Use uppercase letters (A, B, AA, not a, b, aa) |
| `IndexError: list index out of range` | Row number too high | Check that the row exists in the worksheet |

## Performance Considerations

### Reading Large Columns

For columns with thousands of rows, reading all values may be slow:

```bash
# This reads the entire column and filters in Python
python3 read_sheet.py --spreadsheet-id SHEET_ID A

# For very large datasets, consider:
# 1. Reading specific rows only (use the Python API directly)
# 2. Exporting to CSV instead
# 3. Using batch operations
```

### Writing Multiple Cells

For writing many cells, batch operations are more efficient:

```bash
# Instead of looping (slower):
for i in {2..100}; do
    python3 write_sheet.py --spreadsheet-id SHEET_ID A $i "value"
done

# Consider using the gspread Python API directly for batch operations
```

## Integration with CI/CD

These tools can be used in automated workflows:

```bash
#!/bin/bash
# Example: Update build status in a tracking spreadsheet

BUILD_NUMBER=$1
BUILD_STATUS=$2

python3 write_sheet.py \
    --spreadsheet-id 1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI \
    A $BUILD_NUMBER "$BUILD_STATUS"
```

## Best Practices

1. **Always verify credentials first**: Test with a simple read operation before building complex workflows
2. **Use JSON output for programmatic processing**: It's more reliable than parsing plain text
3. **Handle errors gracefully**: Check exit codes (`echo $?`) and retry on rate limit errors
4. **Document your spreadsheet structure**: Include headers and comments about which columns contain which data
5. **Test with a copy**: Before running on production data, test with a backup spreadsheet
6. **Use formatting-only mode carefully**: Remember that omitting `value` applies cell formatting, not clears the cell

## Security Notes

- **Protect service-account.json**: Never commit it to version control or share it
- **Use .gitignore**: Ensure `service-account.json` is in `.gitignore`
- **Limit sheet access**: Share the target spreadsheet only with the specific service account
- **Audit access**: Review the service account activity logs regularly
