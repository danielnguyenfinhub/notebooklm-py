# 540-notebooklm-upload-download-url-hardening-v2

## Summary
Harden all dynamic upload/download URL handling in `notebooklm-py` 0.3.3 while preserving the current UX for normal users.

The current codebase already validates single-file download URLs in `src/notebooklm/_artifacts.py::_download_url`, but it still:
1. sends a raw `Cookie` header to a server-returned `upload_url` in `src/notebooklm/_sources.py`, and
2. performs batch downloads in `src/notebooklm/_artifacts.py::_download_urls_batch` without reusing the same URL validation path.

This spec introduces a shared network-security utility, moves upload flows to domain-scoped `httpx.Cookies`, validates all dynamic URLs, updates docs/config, and replaces insecure unit-test fixtures that currently normalize `https://upload.example.com/...`.

## Why this change
- `notebooklm-py` is an unofficial client built on undocumented Google APIs, so endpoint behavior can change unexpectedly and the client needs stronger defensive validation at trust boundaries.
- Google’s resumable upload flow returns an upload URL in the `x-goog-upload-url` response header; that makes the returned URL a trust boundary.
- `httpx.Cookies` already supports domain-scoped cookies, so there is no need to manually push a full raw `Cookie` header into requests made to dynamic hosts.
- NotebookLM Enterprise now has official APIs for notebooks, sources, and audio overviews; that makes it even more important that the unofficial cookie-based path be explicit about its trust boundaries and blast radius.

## Scope
### In scope
- Shared validation for dynamic upload/download URLs.
- Remove raw `Cookie` header from credentialed upload-to-dynamic-URL requests.
- Reuse cookie jar loading from `auth.py`.
- Strengthen unit coverage and align tests with the hardened behavior.
- Update docs for the new env var override and security rationale.

### Out of scope
- Migrating the library to the official NotebookLM Enterprise APIs.
- Encrypting `storage_state.json` or replacing browser-cookie auth.
- Reworking Playwright login or browser profile storage.

## Current code findings (repo-specific)
### `src/notebooklm/_sources.py`
- `_start_resumable_upload()` posts to fixed `UPLOAD_URL` and reads `x-goog-upload-url`.
- `_upload_file_streaming()` then POSTS to `upload_url` with a manually constructed `Cookie` header.
- There is no host validation for `upload_url`.

### `src/notebooklm/_artifacts.py`
- `_download_url()` validates scheme/domain before sending credentialed requests.
- `_download_urls_batch()` does not validate URLs and duplicates less-safe behavior.

### Tests
- `tests/unit/test_sources_upload.py` currently treats `https://upload.example.com/...` as a normal success path and asserts that `"Cookie"` is present in headers.
- `tests/unit/test_artifacts_coverage.py` uses `https://example.com/...` for batch download success paths, which does not match the current intent of trusted Google-domain-only credentialed downloads.

## Requirements
### R1. Shared validator
Add a shared module (recommended: `src/notebooklm/_netsec.py`) with:
- `validate_trusted_https_url(url, *, purpose, extra_hosts=None)`
- `parse_trusted_extra_hosts_from_env()`
- optional `redact_url_for_logs(url)` helper

The validator must:
- require `https`
- require a hostname
- reject IP literals
- reject embedded username/password
- reject non-443 explicit ports
- allow:
  - `*.google.com`
  - `*.googleusercontent.com`
  - `*.googleapis.com`
  - exact hosts from env override
- raise `ValidationError` with an actionable message

### R2. Upload hardening
Patch `src/notebooklm/_sources.py`:
- validate the returned `upload_url` immediately after reading `x-goog-upload-url`
- validate again before streaming bytes
- remove the manual `"Cookie"` header from requests sent to `upload_url`
- use `load_httpx_cookies()` for the upload client
- set `follow_redirects=False` for the upload-byte POST unless a test demonstrates NotebookLM requires otherwise

### R3. Download hardening
Patch `src/notebooklm/_artifacts.py`:
- refactor `_download_url()` to use the shared validator
- update `_download_urls_batch()` to validate each URL before request dispatch
- keep current behavior of rejecting HTML responses for media downloads
- keep domain-scoped cookie jar usage

### R4. Low-friction override
Add env var:
- `NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS`
Comma-separated exact hostnames only (no wildcards in v2).

Behavior:
- normal users should see no prompts and no config changes on standard Google hosts
- if a new legitimate Google-adjacent host appears, users can temporarily unblock it with one env var
- error messages must include both “upgrade notebooklm-py” and the env var override path

### R5. Tests
Add/modify tests so that:
- insecure hosts are rejected
- known-good Google hosts are accepted
- env override works
- `"Cookie"` is no longer asserted on `upload_url` requests
- upload start remains allowed against fixed `UPLOAD_URL`
- batch download paths validate URLs before request dispatch

### R6. Docs
Update:
- `README.md`
- `SECURITY.md`
- `docs/configuration.md`

Include:
- rationale for the new host validation
- how to use `NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS`
- explicit note that `storage_state.json` remains highly sensitive

## UX / friction budget
### Default user path
Zero additional steps for normal use on current Google hosts.

### Exceptional path
A single explicit override for newly observed legitimate hosts:
```bash
export NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS="new.host.googleapis.com"
```

### Not acceptable
- interactive trust prompts
- “trust forever” writes to local config in v2
- wildcard overrides

## Acceptance criteria
1. A malicious or unexpected `upload_url` such as `https://evil.example.com/session` raises `ValidationError` before any credentialed upload request is sent.
2. `tests/unit/test_sources_upload.py` no longer encodes insecure behavior as the success baseline.
3. `_download_urls_batch()` validates URLs before download.
4. All new tests pass under the repo’s current pytest configuration.
5. Docs clearly explain the override and the security tradeoff.
