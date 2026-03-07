Run a focused validation pass for the URL-hardening patch.

Minimum test plan:
1. `pytest tests/unit/test_netsec.py -q`
2. `pytest tests/unit/test_sources_upload.py -q`
3. `pytest tests/unit/test_artifacts_coverage.py -q`
4. If green, run full unit suite

Manual code review assertions:
- `_upload_file_streaming()` no longer sends `"Cookie"` in headers
- `_start_resumable_upload()` validates `x-goog-upload-url`
- `_download_urls_batch()` validates each URL
- docs mention `NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS`

Report:
- pass/fail by file
- any residual risk
- any test gaps
