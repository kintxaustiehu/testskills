"""Proof-only live integration verification for read_sheet.py and write_sheet.py.

Requires Google Sheets API enabled for the service account project and sheet access.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import gspread

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from read_sheet import get_column_values
from write_sheet import write_cell_value

PYTHON = str(ROOT / '.venv' / 'bin' / 'python')
SPREADSHEET_ID = '1-UmbmMzDj8J9g6aayClqDOvsL0CcWZdnOnHs3bowfgI'
SERVICE_ACCOUNT_PATH = ROOT / 'service-account.json'
MAX_RETRY_ATTEMPTS = 6
INITIAL_BACKOFF_SECONDS = 2.0

assert SERVICE_ACCOUNT_PATH.exists(), 'Missing service-account.json'
assert (ROOT / 'read_sheet.py').exists(), 'Missing read_sheet.py'
assert (ROOT / 'write_sheet.py').exists(), 'Missing write_sheet.py'

service_account_data = json.loads(SERVICE_ACCOUNT_PATH.read_text(encoding='utf-8'))
project_id = service_account_data.get('project_id', '')
client_email = service_account_data.get('client_email', '')


def _column_index_to_letter(column_index: int) -> str:
    """Convert a 1-based column index to A1 column letters."""
    if column_index < 1:
        raise ValueError('column_index must be >= 1')

    letters = []
    current = column_index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        letters.append(chr(ord('A') + remainder))
    return ''.join(reversed(letters))


def _activation_url_from_exception(exc: Exception) -> str | None:
    """Extract the API activation URL from a gspread chained exception if present."""
    response = getattr(exc, 'response', None)
    if response is None:
        cause = getattr(exc, '__cause__', None)
        response = getattr(cause, 'response', None) if cause is not None else None
    if response is None:
        return None

    try:
        payload = response.json()
    except Exception:
        return None

    details = payload.get('error', {}).get('details', [])
    for detail in details:
        metadata = detail.get('metadata', {})
        url = metadata.get('activationUrl')
        if url:
            return url

    for detail in details:
        for link in detail.get('links', []):
            url = link.get('url')
            if url:
                return url

    return None


def _is_retryable_quota_error(message: str) -> bool:
    lower = message.lower()
    return (
        '[429]' in message
        or 'quota exceeded' in lower
        or 'resource_exhausted' in lower
        or 'too many requests' in lower
        or 'read requests per minute' in lower
    )


def _run_gspread_with_retry(operation_name: str, operation, max_attempts: int = MAX_RETRY_ATTEMPTS):
    delay_seconds = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except gspread.exceptions.APIError as exc:
            if attempt < max_attempts and _is_retryable_quota_error(str(exc)):
                print(
                    f'WARN: {operation_name} hit quota. Retrying in {delay_seconds:.1f}s '
                    f'(attempt {attempt}/{max_attempts})...',
                    file=sys.stderr,
                )
                time.sleep(delay_seconds)
                delay_seconds *= 2
                continue
            raise


def _open_spreadsheet_with_retry(client_obj, spreadsheet_id: str, max_attempts: int = MAX_RETRY_ATTEMPTS):
    delay_seconds = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, max_attempts + 1):
        try:
            return client_obj.open_by_key(spreadsheet_id)
        except (PermissionError, gspread.exceptions.APIError) as exc:
            cause = getattr(exc, '__cause__', None)
            cause_message = str(cause) if cause is not None else str(exc)
            if attempt < max_attempts and _is_retryable_quota_error(cause_message):
                print(
                    f'WARN: open_by_key hit quota. Retrying in {delay_seconds:.1f}s '
                    f'(attempt {attempt}/{max_attempts})...',
                    file=sys.stderr,
                )
                time.sleep(delay_seconds)
                delay_seconds *= 2
                continue
            raise

# Live auth + worksheet context
client = gspread.service_account(filename=str(SERVICE_ACCOUNT_PATH))
try:
    spreadsheet = _open_spreadsheet_with_retry(client, SPREADSHEET_ID)
except (PermissionError, gspread.exceptions.APIError) as exc:
    cause = getattr(exc, '__cause__', None)
    activation_url = _activation_url_from_exception(exc)
    print('ERROR: Could not open spreadsheet in live verification.', file=sys.stderr)
    if cause is not None:
        print(f'Cause: {cause}', file=sys.stderr)
    else:
        print(f'Cause: {exc}', file=sys.stderr)
    if activation_url:
        print(f'Enable Google Sheets API for this project: {activation_url}', file=sys.stderr)
    elif project_id:
        print(
            'Enable Google Sheets API for this project: '
            f'https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project={project_id}',
            file=sys.stderr,
        )
    if client_email:
        print(
            f'Share the spreadsheet with the service account email: {client_email}',
            file=sys.stderr,
        )
    print('If you enabled API access recently, wait a few minutes and retry.', file=sys.stderr)
    raise SystemExit(1) from exc

first_ws = _run_gspread_with_retry('get_worksheet(0)', lambda: spreadsheet.get_worksheet(0))
assert first_ws is not None, 'No first worksheet found'
first_ws_title = first_ws.title

results = []

def run_cmd(args):
    delay_seconds = INITIAL_BACKOFF_SECONDS
    max_attempts = MAX_RETRY_ATTEMPTS
    for attempt in range(1, max_attempts + 1):
        completed = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
        if completed.returncode == 0:
            return completed.stdout.strip()

        combined_output = f"{completed.stdout}\n{completed.stderr}"
        if attempt < max_attempts and _is_retryable_quota_error(combined_output):
            print(
                f'WARN: command hit quota. Retrying in {delay_seconds:.1f}s '
                f'(attempt {attempt}/{max_attempts})...',
                file=sys.stderr,
            )
            time.sleep(delay_seconds)
            delay_seconds *= 2
            continue

        cmd = ' '.join(args)
        raise RuntimeError(
            f'Command failed: {cmd}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}'
        )

# Requirement checks via direct function behavior (read)
rows = _run_gspread_with_retry(
    'get_column_values(A)',
    lambda: get_column_values(SPREADSHEET_ID, 'A'),
)
assert isinstance(rows, list), 'get_column_values should return a list'
assert all(isinstance(t, tuple) and len(t) == 2 for t in rows), 'Rows must be (row, value) tuples'
assert all(isinstance(r, int) and r >= 1 for r, _ in rows), 'Row numbers must be 1-indexed ints'
assert all(isinstance(v, str) and v.strip() != '' for _, v in rows), 'Only non-empty values should be included'
results.append('PASS: read_sheet.get_column_values returns non-empty (row, value) tuples with 1-index rows')

# CLI default output format
plain_out = run_cmd([PYTHON, 'read_sheet.py', '--spreadsheet-id', SPREADSHEET_ID, 'A'])
if plain_out:
    first_line = plain_out.splitlines()[0]
    assert re.match(r'^\d+:\s', first_line), f'Unexpected plain output format: {first_line!r}'
results.append('PASS: read_sheet.py default output matches "{row}: {value}" format')

# CLI JSON output format + optional worksheet positional
json_out = run_cmd([
    PYTHON,
    'read_sheet.py',
    '--spreadsheet-id',
    SPREADSHEET_ID,
    'A',
    first_ws_title,
    '--json',
])
parsed = json.loads(json_out)
assert isinstance(parsed, list), '--json output must be a JSON array'
if parsed:
    assert {'row', 'value'} <= set(parsed[0].keys()), 'JSON objects must contain row and value keys'
results.append('PASS: read_sheet.py --json outputs JSON array of {row, value}')
results.append('PASS: read_sheet.py accepts optional worksheet positional argument')

# Prepare a safe in-grid test cell and avoid collisions across repeated runs.
if first_ws.col_count < 1 or first_ws.row_count < 1:
    raise RuntimeError('Worksheet grid is invalid: row_count/col_count must be >= 1')

seed = int(time.time() * 1000) ^ os.getpid()
test_col_idx = (seed % first_ws.col_count) + 1
test_row = ((seed // max(1, first_ws.col_count)) % first_ws.row_count) + 1
test_col = _column_index_to_letter(test_col_idx)
test_addr = f'{test_col}{test_row}'
marker_value = f'copilot-proof-{int(time.time())}'
original_value = _run_gspread_with_retry(
    f'acell({test_addr}) initial read',
    lambda: first_ws.acell(test_addr).value,
)

try:
    # Write with value through function and verify cell value changed
    addr = _run_gspread_with_retry(
        f'write_cell_value({test_addr}) function write',
        lambda: write_cell_value(SPREADSHEET_ID, test_col, test_row, marker_value, worksheet_name=first_ws_title),
    )
    assert addr == test_addr, f'Expected returned address {test_addr}, got {addr}'
    read_back = _run_gspread_with_retry(
        f'acell({test_addr}) after function write',
        lambda: first_ws.acell(test_addr).value,
    )
    assert read_back == marker_value, f'Expected cell value {marker_value!r}, got {read_back!r}'
    results.append('PASS: write_sheet.write_cell_value writes value and returns correct A1 address')

    # CLI write with value and worksheet argument
    cli_written = run_cmd([
        PYTHON,
        'write_sheet.py',
        '--spreadsheet-id', SPREADSHEET_ID,
        test_col,
        str(test_row),
        marker_value + '-cli',
        first_ws_title,
    ])
    assert f'Written to cell {test_addr}.' in cli_written, f'Unexpected confirmation: {cli_written!r}'
    read_back_cli = _run_gspread_with_retry(
        f'acell({test_addr}) after CLI write',
        lambda: first_ws.acell(test_addr).value,
    )
    assert read_back_cli == marker_value + '-cli', 'CLI write did not update expected value'
    results.append('PASS: write_sheet.py writes via CLI and prints confirmation')

    # CLI formatting-only branch (value omitted) should not overwrite value
    before = _run_gspread_with_retry(
        f'acell({test_addr}) before formatting-only CLI run',
        lambda: first_ws.acell(test_addr).value,
    )
    cli_format_only = run_cmd([
        PYTHON,
        'write_sheet.py',
        '--spreadsheet-id', SPREADSHEET_ID,
        test_col,
        str(test_row),
    ])
    assert f'Written to cell {test_addr}.' in cli_format_only, 'Formatting-only run missing confirmation message'
    after = _run_gspread_with_retry(
        f'acell({test_addr}) after formatting-only CLI run',
        lambda: first_ws.acell(test_addr).value,
    )
    assert before == after, 'Formatting-only mode overwrote existing cell value'
    results.append('PASS: write_sheet.py formatting-only mode preserves existing cell value')
finally:
    # Restore the test cell so repeated verifications are minimally invasive.
    if original_value is None:
        _run_gspread_with_retry(
            f'batch_clear({test_addr}) restore',
            lambda: first_ws.batch_clear([test_addr]),
        )
    else:
        _run_gspread_with_retry(
            f'update({test_addr}) restore',
            lambda: first_ws.update(range_name=test_addr, values=[[original_value]]),
        )

# Static source checks for exact required API calls
read_src = (ROOT / 'read_sheet.py').read_text(encoding='utf-8')
write_src = (ROOT / 'write_sheet.py').read_text(encoding='utf-8')
assert 'worksheet.col_values(col_idx)' in read_src, 'read_sheet.py must use worksheet.col_values(col_idx)'
assert 'worksheet.update(range_name=cell_address, values=[[value]])' in write_src, 'write_sheet.py must call worksheet.update(range_name=<addr>, values=[[value]])'
results.append('PASS: required gspread call signatures are present in source')

print('VERIFICATION RESULTS')
for line in results:
    print(line)
print(f'TEST CELL USED: {first_ws_title}!{test_addr}')
