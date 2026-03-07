Implement the OpenSpec exactly, but prefer the smallest correct patch.

Checklist:
1. Add `src/notebooklm/_netsec.py`
2. Harden `src/notebooklm/_sources.py`
3. Refactor `src/notebooklm/_artifacts.py`
4. Update/add unit tests
5. Update docs

Implementation guidance:
- Dynamic upload hosts are a trust boundary; validate twice (after header extraction and before streaming).
- Do not keep the old test contract that requires raw `"Cookie"` on dynamic upload requests.
- For upload start against fixed `UPLOAD_URL`, preserve existing behavior unless there is a compelling reason to change it.
- Keep override handling env-only in v2; do not add persistent config writes.

Quality bar:
- no regressions to the public API
- minimal diff
- clean error messages
