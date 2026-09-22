# VLCoach agent contract

This file is the shared project contract for Codex, Claude Code, GitHub Copilot, Antigravity, and other coding agents. Harness-specific files may add adapter details, but must not contradict this file.

## Project invariants

- Keep code, comments, documentation, and commit messages in English.
- Use `Scrapling DynamicFetcher` only for collection. Never use stealth fetchers, proxies, CAPTCHA handling, fingerprint spoofing, or Tracker Network internal APIs.
- Fail closed on access blocks. Do not escalate retries.
- Never fabricate missing values or infer a match result that the source page did not state.
- Preserve the pipeline boundary: `collect` writes raw snapshots, `clean` produces typed rows, `stats` computes evidence, and `coach` only phrases computed evidence.
- Keep AI local and optional. Ollama may phrase computed evidence, but deterministic fallback output must remain valid.
- Prefer the standard library and existing dependencies over adding new dependencies.
- Do not modify unrelated files or remove existing user changes.

## Shared workflow

Use the workflow that matches the request:

- Design change: brainstorm the approach, record the decision, then write or update a plan.
- Multi-step work: use an implementation plan under `docs/superpowers/plans/`.
- New behavior: write a failing test first when practical, implement the smallest change, then verify it.
- Bug: reproduce it with a regression test, fix the root cause, and rerun the focused test.
- Scraping or parsing: preserve raw snapshots and test against fixtures and source evidence.
- Statistics: validate sample sizes, bounds, uncertainty intervals, and association-versus-causation claims.
- AI coaching: ensure the model receives computed analysis rather than raw HTML, and validate the fallback.
- Refactor: preserve public behavior and run the affected tests.
- Review: prioritize correctness, provenance, security, regressions, and missing tests.

Before editing, identify the owning module and state the validation command. After editing, run the narrowest relevant check, then review the result from a fresh perspective. When acceptance criteria are ambiguous, ask before changing behavior.

## Agent capability boundary

ECC and Superpowers provide workflows and guidance; they do not replace engineering judgment. Select relevant skills instead of loading every workflow. Claude Code and Codex may invoke native skills, commands, and hooks. Copilot and Antigravity must follow this contract through their project instruction or rule adapters and do not automatically gain every ECC runtime capability.