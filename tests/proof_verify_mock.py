"""Proof-only offline verification for read_sheet.py and write_sheet.py.

This script uses mocks and does not call Google APIs.
"""

import inspect
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import read_sheet
import write_sheet

results = []

# 1) Required function signatures exist
try:
    sig_read = inspect.signature(read_sheet.get_column_values)
    sig_write = inspect.signature(write_sheet.write_cell_value)
    assert list(sig_read.parameters.keys()) == ['spreadsheet_id', 'column_letter', 'worksheet_name']
    assert list(sig_write.parameters.keys()) == ['spreadsheet_id', 'column_letter', 'row_number', 'value', 'worksheet_name']
    results.append('PASS: Required reusable functions and signatures are present')
except Exception as e:
    results.append(f'FAIL: Required reusable functions and signatures are present - {e}')

# 2) read_sheet.get_column_values behavior and required API usage
try:
    with patch('read_sheet.gspread.service_account') as sa:
        worksheet = MagicMock()
        worksheet.col_values.return_value = ['h', '', 'x', '   ', 'y']
        spreadsheet = MagicMock()
        spreadsheet.get_worksheet.return_value = worksheet
        sa.return_value.open_by_key.return_value = spreadsheet

        out = read_sheet.get_column_values('sid', 'A')

        sa.assert_called_once_with(filename='service-account.json')
        sa.return_value.open_by_key.assert_called_once_with('sid')
        spreadsheet.get_worksheet.assert_called_once_with(0)
        worksheet.col_values.assert_called_once_with(1)
        assert out == [(1, 'h'), (3, 'x'), (5, 'y')]
    results.append('PASS: read function authenticates correctly, uses col_values, returns non-empty tuples with 1-index rows')
except Exception as e:
    results.append(f'FAIL: read function authenticates correctly - {e}')

# 3) read_sheet CLI plain format
try:
    with patch('read_sheet.get_column_values', return_value=[(2, 'alpha'), (5, 'beta')]):
        with patch.object(sys, 'argv', ['read_sheet.py', '--spreadsheet-id', 'sid', 'A']):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = read_sheet.main()
            assert code == 0
            assert buf.getvalue().strip().splitlines() == ['2: alpha', '5: beta']
    results.append('PASS: read CLI default output format is {row}: {value}')
except Exception as e:
    results.append(f'FAIL: read CLI default output format - {e}')

# 4) read_sheet CLI JSON format
try:
    with patch('read_sheet.get_column_values', return_value=[(2, 'alpha')]):
        with patch.object(sys, 'argv', ['read_sheet.py', '--spreadsheet-id', 'sid', 'A', '--json']):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = read_sheet.main()
            assert code == 0
            payload = json.loads(buf.getvalue())
            assert payload == [{'row': 2, 'value': 'alpha'}]
            assert '\n  {' in buf.getvalue()
    results.append('PASS: read CLI JSON output is pretty-printed array of {row, value}')
except Exception as e:
    results.append(f'FAIL: read CLI JSON output - {e}')

# 5) read_sheet optional worksheet positional
try:
    with patch('read_sheet.gspread.service_account') as sa:
        worksheet = MagicMock()
        worksheet.col_values.return_value = []
        spreadsheet = MagicMock()
        spreadsheet.worksheet.return_value = worksheet
        sa.return_value.open_by_key.return_value = spreadsheet

        _ = read_sheet.get_column_values('sid', 'I', 'Tab1')
        spreadsheet.worksheet.assert_called_once_with('Tab1')
    results.append('PASS: read function supports optional worksheet name')
except Exception as e:
    results.append(f'FAIL: read function supports optional worksheet name - {e}')

# 6) write_sheet write path with update(range_name=..., values=[[value]])
try:
    with patch('write_sheet.gspread.service_account') as sa:
        worksheet = MagicMock()
        spreadsheet = MagicMock()
        spreadsheet.get_worksheet.return_value = worksheet
        sa.return_value.open_by_key.return_value = spreadsheet

        addr = write_sheet.write_cell_value('sid', 'I', 5, 'hello')
        assert addr == 'I5'
        worksheet.update.assert_called_once_with(range_name='I5', values=[['hello']])
        worksheet.format.assert_not_called()
    results.append('PASS: write function writes with required worksheet.update signature and returns A1 address')
except Exception as e:
    results.append(f'FAIL: write function writes - {e}')

# 7) write_sheet formatting-only path does not call update
try:
    with patch('write_sheet.gspread.service_account') as sa:
        worksheet = MagicMock()
        spreadsheet = MagicMock()
        spreadsheet.get_worksheet.return_value = worksheet
        sa.return_value.open_by_key.return_value = spreadsheet

        addr = write_sheet.write_cell_value('sid', 'AA', 12, None)
        assert addr == 'AA12'
        worksheet.update.assert_not_called()
        worksheet.format.assert_called_once()
    results.append('PASS: write function formatting-only mode avoids overwriting value')
except Exception as e:
    results.append(f'FAIL: write function formatting-only mode - {e}')

# 8) write_sheet optional worksheet positional and CLI confirmation
try:
    with patch('write_sheet.gspread.service_account') as sa:
        worksheet = MagicMock()
        spreadsheet = MagicMock()
        spreadsheet.worksheet.return_value = worksheet
        sa.return_value.open_by_key.return_value = spreadsheet

        _ = write_sheet.write_cell_value('sid', 'B', 9, 'v', 'TabX')
        spreadsheet.worksheet.assert_called_once_with('TabX')
    results.append('PASS: write function supports optional worksheet name')
except Exception as e:
    results.append(f'FAIL: write function optional worksheet - {e}')

try:
    with patch('write_sheet.write_cell_value', return_value='I5'):
        with patch.object(sys, 'argv', ['write_sheet.py', '--spreadsheet-id', 'sid', 'I', '5', 'hello']):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = write_sheet.main()
            assert code == 0
            assert buf.getvalue().strip() == 'Written to cell I5.'
    results.append('PASS: write CLI prints required confirmation message')
except Exception as e:
    results.append(f'FAIL: write CLI - {e}')

print('MOCK VERIFICATION RESULTS')
for r in results:
    print(r)
