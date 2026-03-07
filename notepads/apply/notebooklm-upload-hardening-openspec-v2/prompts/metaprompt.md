You are the lead engineer for this patch.

Objective:
Land the OpenSpec bundle for URL hardening in `notebooklm-py` 0.3.3 with minimal surface area and no unnecessary UX friction.

Execution order:
1. Read spec + changelist + tasks
2. Patch code
3. Patch tests
4. Patch docs
5. Run focused tests
6. Summarize delta and residual risk

Decision policy:
- Prefer shared helpers over duplicated inline validation
- Prefer exact host overrides over wildcards
- Prefer failing closed with actionable messaging
- Preserve stable APIs and current CLI ergonomics
- Be explicit when the repo’s current tests encode insecure assumptions, and replace those assumptions rather than preserving them

Final output:
- concise implementation summary
- files changed
- tests run
- residual risk / follow-up items
