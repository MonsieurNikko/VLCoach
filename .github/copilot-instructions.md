# VLCoach project instructions

## Project constraints

- Keep all code, comments, documentation, and commits in English.
- Use `Scrapling DynamicFetcher` or `StealthyFetcher` for collection. v0.2 uses `DynamicFetcher` only; switch after an observed block, recorded as a design change.
- Fail closed when access is blocked. Do not escalate retries.
- Never fabricate missing values or infer match results that the source page does not state.
- Preserve the pipeline boundary: collect writes raw snapshots, clean produces typed rows, stats computes evidence, and coach only phrases computed evidence.
- Keep the local-only AI design: Ollama is optional, and reports must retain a deterministic fallback.

## Engineering workflow

- Before implementing a feature, identify the owning module and write a short plan.
- For behavior changes, reproduce the behavior with a failing test before implementation when practical.
- Make the smallest focused change, then run the narrowest relevant test or validation command.
- Review the change from a fresh perspective for regressions, fabricated data, uncertainty loss, and privacy issues.
- Do not add dependencies when the standard library or an existing project dependency is sufficient.
- Do not modify unrelated files or remove user changes.

## Dynamic workflow selection

Choose the workflow that matches the task:

- New feature: plan first, then test-driven implementation and focused verification.
- Bug: reproduce with a failing regression test, fix the root cause, then rerun the test.
- Scraping or parsing: inspect the source evidence and add fixture-based tests; preserve raw snapshots.
- Statistics: validate sample sizes, bounds, uncertainty intervals, and no-causation claims.
- AI coaching: verify that the model receives computed analysis rather than raw HTML and that fallback output remains valid.
- Refactor: preserve public behavior and run the affected test suite.
- Review: prioritize correctness, data provenance, security, and missing tests.

When a task is ambiguous, ask for the missing acceptance criteria before changing code. State the chosen workflow and validation command briefly in the response.