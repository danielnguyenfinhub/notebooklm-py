# Plan

## Phase 1 — Shared validator
1. Add `src/notebooklm/_netsec.py`.
2. Implement strict URL parsing/validation + env override parsing.
3. Keep the API tiny and dependency-free.

## Phase 2 — Upload flow hardening
1. Patch `_start_resumable_upload()` to validate `x-goog-upload-url`.
2. Patch `_upload_file_streaming()` to validate again before POST.
3. Switch dynamic upload requests from raw `Cookie` header to `load_httpx_cookies()`.

## Phase 3 — Download flow unification
1. Replace inline validation in `_download_url()` with the shared helper.
2. Validate each URL inside `_download_urls_batch()`.

## Phase 4 — Tests
1. Add new validator tests.
2. Update `test_sources_upload.py` expectations and hosts.
3. Update `test_artifacts_coverage.py` batch download hosts and failure cases.

## Phase 5 — Docs
1. README security note
2. SECURITY.md supported versions + trusted-host override
3. docs/configuration.md env var reference

## Phase 6 — Quality gate
1. Run focused unit tests first.
2. Then run the full unit suite.
3. Ensure no new lint/type issues in touched files.
