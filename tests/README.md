# Verification Scripts (Proof Only)

These scripts are only for proving that `read_sheet.py` and `write_sheet.py`
match the requested requirements.

## Files

- `proof_verify_mock.py`: offline proof using mocks (no Google API calls).
- `proof_verify_live.py`: live integration proof against Google Sheets.

## Recommended usage

Run from the project root:

```bash
.venv/bin/python tests/proof_verify_mock.py
```

For live verification (requires Sheets API enabled and spreadsheet access for the service account):

```bash
.venv/bin/python tests/proof_verify_live.py
```

## Troubleshooting live verification

If `proof_verify_live.py` fails with `PermissionError`, the most common causes are:

- Google Sheets API is disabled in the service-account project.
- The spreadsheet is not shared with the service-account email.

Enable the API for your project and then retry:

https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=533943120652
