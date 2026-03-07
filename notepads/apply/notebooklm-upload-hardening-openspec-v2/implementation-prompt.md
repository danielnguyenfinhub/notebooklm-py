# Implementation prompt: 540-notebooklm-upload-download-url-hardening-v2

**Role:** You are the implementer for the NotebookLM upload/download URL hardening OpenSpec. Prefer the smallest correct patch. Read the spec first and treat the written spec as the source of truth over any summary below.

**Objective:** Harden all dynamic upload/download URL handling in `notebooklm-py` 0.3.3 while preserving current UX for normal users. Introduce a shared network-security utility, move upload flows to domain-scoped `httpx.Cookies`, validate all dynamic URLs, update docs, and replace insecure unit-test fixtures.

## Spec files (read first)

- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/spec.md` — requirements, scope, acceptance criteria
- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/changes.md` — file-by-file changelist
- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/plan.md` — phases
- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/tasks.md` — task checklist
- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/acceptance_tests.md` — acceptance tests

## Non-negotiables

- No raw `Cookie` header sent to dynamic upload hosts; use `load_httpx_cookies()` for upload client.
- Validate every dynamic upload/download URL (after `x-goog-upload-url` and before streaming; before each batch download).
- Tests must not treat `upload.example.com` or `example.com` as normative success cases for credentialed flows.
- Error messages must include both “upgrade notebooklm-py” and the env var override path.
- No new runtime dependencies; preserve public APIs and CLI UX.
- Override is env-only in v2: `NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS`; no persistent config writes or interactive trust prompts.

## Implementation order

1. **Phase 1 — Shared validator:** Add `src/notebooklm/_netsec.py`; implement strict URL validation and env override parsing.
2. **Phase 2 — Upload hardening:** Patch `_start_resumable_upload()` and `_upload_file_streaming()`; switch to `load_httpx_cookies()`; validate upload URL twice.
3. **Phase 3 — Download unification:** Refactor `_download_url()` to use shared validator; validate each URL in `_download_urls_batch()`.
4. **Phase 4 — Tests:** Add `tests/unit/test_netsec.py`; update `test_sources_upload.py` and `test_artifacts_coverage.py`.
5. **Phase 5 — Docs:** README security note; SECURITY.md; `docs/configuration.md` env var.
6. **Phase 6 — Quality gate:** Run focused unit tests then full suite; ensure no new lint/type issues.

## Deliverables and paths

| Deliverable | Paths |
|-------------|--------|
| New module | `src/notebooklm/_netsec.py` |
| Patched code | `src/notebooklm/_sources.py`, `src/notebooklm/_artifacts.py` |
| New/updated tests | `tests/unit/test_netsec.py`, `tests/unit/test_sources_upload.py`, `tests/unit/test_artifacts_coverage.py` |
| Docs | `README.md`, `SECURITY.md`, `docs/configuration.md` |

## Acceptance criteria (from spec)

1. A malicious or unexpected `upload_url` (e.g. `https://evil.example.com/session`) raises `ValidationError` before any credentialed upload request.
2. `tests/unit/test_sources_upload.py` no longer encodes insecure behavior as the success baseline.
3. `_download_urls_batch()` validates URLs before download.
4. All new tests pass under the repo’s current pytest configuration.
5. Docs clearly explain the override and the security tradeoff.

Stop when the focused tests in the spec are green or you can explain precisely what remains blocked.
