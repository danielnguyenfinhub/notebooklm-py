# Acceptance tests

## AT1 — Untrusted upload URL rejected
Given `_start_resumable_upload()` receives:
`x-goog-upload-url: https://evil.example.com/session`
Then it raises `ValidationError` before any dynamic upload POST occurs.

## AT2 — Dynamic upload request does not use raw Cookie header
Given `_upload_file_streaming()` is called with a trusted host
Then request headers do not contain `"Cookie"`
And `httpx.AsyncClient(..., cookies=load_httpx_cookies())` is used.

## AT3 — Trusted hosts accepted
The following validate successfully:
- `https://notebooklm.google.com/...`
- `https://upload.googleusercontent.com/...`
- `https://content.googleapis.com/...`

## AT4 — Override works
Given:
```bash
export NOTEBOOKLM_TRUSTED_UPLOAD_HOSTS="upload.example.com"
```
Then:
`https://upload.example.com/session123`
validates successfully.

## AT5 — Batch downloads validate URLs
Given `_download_urls_batch()` receives one trusted URL and one untrusted URL
Then the untrusted URL path is rejected and the trusted path remains covered by tests.

## AT6 — Docs updated
README, SECURITY.md, and docs/configuration.md all document:
- trusted host enforcement
- env override
- continued sensitivity of auth state

## AT7 — Repo test conventions preserved
Focused tests pass with the existing pytest setup in `pyproject.toml`.
