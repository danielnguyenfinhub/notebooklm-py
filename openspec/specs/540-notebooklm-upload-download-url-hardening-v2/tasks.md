# Tasks

## T1. Add shared network security helper
- [x] Create `src/notebooklm/_netsec.py`
- [x] Add validator + env parser
- [x] Add docstrings and tight error messages

## T2. Harden resumable upload flow
- [x] Patch `_start_resumable_upload()`
- [x] Patch `_upload_file_streaming()`
- [x] Switch dynamic upload requests to `load_httpx_cookies()`
- [x] Ensure no raw `Cookie` header is sent to dynamic upload hosts

## T3. Unify download validation
- [x] Refactor `_download_url()` to use shared validator
- [x] Validate URLs in `_download_urls_batch()`
- [x] Preserve existing HTML/media checks

## T4. Update tests
- [x] Add `tests/unit/test_netsec.py`
- [x] Update `tests/unit/test_sources_upload.py`
- [x] Update `tests/unit/test_artifacts_coverage.py`
- [x] Keep mocks idiomatic for existing test style

## T5. Update docs
- [x] README security note
- [x] SECURITY.md refresh
- [x] docs/configuration.md env var docs

## T6. Verification
- [x] Run `pytest tests/unit/test_netsec.py`
- [x] Run `pytest tests/unit/test_sources_upload.py tests/unit/test_artifacts_coverage.py`
- [x] Run full unit suite
