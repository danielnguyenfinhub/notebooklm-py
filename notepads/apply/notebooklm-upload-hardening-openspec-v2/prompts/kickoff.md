You are modifying `notebooklm-py` 0.3.3.

Read these files first:
- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/spec.md`
- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/changes.md`
- `openspec/specs/540-notebooklm-upload-download-url-hardening-v2/tasks.md`
- `docs/development.md`
- `SECURITY.md`

Goal:
Harden dynamic upload/download URL handling without adding friction for standard users.

Important repo-specific constraints:
- Follow existing module layout under `src/notebooklm/`
- Use current exception types (`ValidationError`, `SourceAddError`, `ArtifactDownloadError`) appropriately
- Preserve current public APIs and CLI UX
- Match existing pytest style and mocking conventions
- Do not add new runtime dependencies

Deliverables:
1. Code changes
2. Tests
3. Docs
4. Short implementation notes describing any judgment calls

Stop only when the focused tests in the spec are green or you can explain precisely what remains blocked.
