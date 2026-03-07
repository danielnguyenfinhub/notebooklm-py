# Tasks

## T1. Add shared network security helper
- [ ] Create `src/notebooklm/_netsec.py`
- [ ] Add validator + env parser
- [ ] Add docstrings and tight error messages

## T2. Harden resumable upload flow
- [ ] Patch `_start_resumable_upload()`
- [ ] Patch `_upload_file_streaming()`
- [ ] Switch dynamic upload requests to `load_httpx_cookies()`
- [ ] Ensure no raw `Cookie` header is sent to dynamic upload hosts

## T3. Unify download validation
- [ ] Refactor `_download_url()` to use shared validator
- [ ] Validate URLs in `_download_urls_batch()`
- [ ] Preserve existing HTML/media checks

## T4. Update tests
- [ ] Add `tests/unit/test_netsec.py`
- [ ] Update `tests/unit/test_sources_upload.py`
- [ ] Update `tests/unit/test_artifacts_coverage.py`
- [ ] Keep mocks idiomatic for existing test style

## T5. Update docs
- [ ] README security note
- [ ] SECURITY.md refresh
- [ ] docs/configuration.md env var docs

## T6. Verification
- [ ] Run `pytest tests/unit/test_netsec.py`
- [ ] Run `pytest tests/unit/test_sources_upload.py tests/unit/test_artifacts_coverage.py`
- [ ] Run full unit suite
