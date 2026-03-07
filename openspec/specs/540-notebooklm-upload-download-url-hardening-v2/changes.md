# File-by-file changelist

## New file
### `src/notebooklm/_netsec.py`
Add:
- `DEFAULT_TRUSTED_SUFFIXES = (".google.com", ".googleusercontent.com", ".googleapis.com")`
- `parse_trusted_extra_hosts_from_env()`
- `validate_trusted_https_url(url, *, purpose, extra_hosts=None)`
- `redact_url_for_logs(url)` (optional but recommended)

Implementation notes:
- use `urllib.parse.urlparse`
- use `ipaddress.ip_address()` to reject IP literals
- normalize hostname to lowercase
- reject `username`, `password`, and explicit non-443 ports
- exact-match only for env override hosts

## Modified files
### `src/notebooklm/_sources.py`
Change `_start_resumable_upload()`:
- after reading `x-goog-upload-url`, call `validate_trusted_https_url(..., purpose="resumable upload start")`

Change `_upload_file_streaming()`:
- validate `upload_url` again before streaming
- remove `"Cookie": self._core.auth.cookie_header` from headers
- load `cookies = load_httpx_cookies()`
- instantiate `httpx.AsyncClient(timeout=300.0, cookies=cookies, follow_redirects=False)`

Do **not** change the fixed `UPLOAD_URL` request path unless required for consistency; the trust boundary is the returned dynamic `upload_url`, not the hard-coded NotebookLM upload entrypoint.

### `src/notebooklm/_artifacts.py`
Change `_download_url()`:
- replace inline domain/scheme logic with `validate_trusted_https_url(..., purpose="artifact download")`

Change `_download_urls_batch()`:
- validate every URL before `client.get(url)`
- use the same helper as `_download_url()`
- preserve existing HTML-response rejection

Optional cleanup:
- fix the misleading inline comment implying `httpx` sends cookies to every domain indiscriminately

### `tests/unit/test_sources_upload.py`
Update these expectations:
- success-path hosts should use trusted domains such as:
  - `https://upload.googleusercontent.com/session123`
  - `https://content.googleapis.com/upload/session123`
- add negative tests for `https://upload.example.com/session123`
- remove assertions that `"Cookie"` exists on the dynamic upload request
- add assertions that `AsyncClient` is created with `cookies=...`
- add env override test using `monkeypatch.setenv("NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS", ...)`

### `tests/unit/test_artifacts_coverage.py`
Update `_download_urls_batch()` tests:
- trusted hosts only in success paths
- explicit rejection test for untrusted hosts
- patch the shared validator or use real validator behavior

### `tests/unit/test_netsec.py` (new)
Add focused unit tests for:
- https required
- hostname required
- IP literals rejected
- userinfo rejected
- non-443 port rejected
- trusted Google hosts accepted
- override host accepted
- evil host rejected

### `README.md`
Add a short security note under authentication / security sections:
- dynamic upload/download URLs are restricted to trusted Google hosts
- use env override only when necessary and temporarily

### `SECURITY.md`
Update:
- supported versions table (currently stale)
- add a note about trusted-host validation
- clarify that `NOTEBOOKLM_AUTH_JSON` is still sensitive even if file-free

### `docs/configuration.md`
Add env var row:
- `NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS`

Document example:
```bash
export NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS="new.host.googleapis.com"
```

## Explicitly remove / replace
- tests that treat `upload.example.com` or `example.com` as normative success cases for credentialed upload/download flows
- assertions that raw `Cookie` must be present on requests to dynamic upload hosts
