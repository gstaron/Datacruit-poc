# Security & code review process

This document describes what's already wired up in this repo, and how
to layer Claude-powered agents on top for continuous, automated review.

## What's already automated (`.github/workflows/`)

- **`backend-ci.yml`** — on every push/PR touching `backend/`: runs the
  full test suite with **100% coverage enforced** (`pytest` fails the
  build below that threshold, see `backend/pyproject.toml`), then
  `bandit` (static analysis for common Python/Django security mistakes)
  and `pip-audit` (checks pinned dependencies against known CVE
  databases). Both scanners currently report zero findings.
- **`security-scan.yml`** — the same two scanners, but on a **weekly
  schedule** independent of code changes, because a dependency can
  become vulnerable overnight even if nobody touched the code (a CVE
  gets published against a package already pinned in `requirements.txt`).
- **`dependabot.yml`** — automated weekly PRs bumping vulnerable/outdated
  dependencies for pip (backend), npm (frontend) and the GitHub Actions
  themselves.

This is the deterministic, fast layer: it catches known vulnerability
patterns and known-CVE dependencies reliably and cheaply. It will not
catch a subtle authorization bug or business-logic flaw specific to this
codebase — that needs a second, context-aware layer.

## Adding a Claude-powered code review agent

Two ways to get automated PR review, from least to most setup:

1. **Claude Code Review (GitHub App).** Install the Claude GitHub App
   on the repository (an org admin installs it once, at
   `github.com/apps/claude/installations/select_target`). Once
   installed, it automatically reviews every PR, posts inline comments
   graded by severity (blocking findings vs. optional nits vs.
   pre-existing issues it flags but doesn't block on), and exposes a
   **"Claude Approvals"** status check you can make required in branch
   protection — so a PR can't merge with an unresolved blocking finding.
   This is the lowest-effort option: no workflow YAML to maintain.

2. **`anthropics/claude-code-action` (custom workflow).** For more
   control — e.g. triggering only on certain paths, or running Claude
   Code with a repo-specific review checklist — add a workflow that
   runs the action on `pull_request` events (or on an `@claude` comment
   trigger) with a prompt like `/code-review` or a custom instruction.
   This is what to reach for if the built-in app's behavior doesn't fit
   (e.g. you want a stricter/looser bar than its defaults, or you want
   it to also run project-specific lint rules from a `CLAUDE.md`).

Either way, pair it with the human review this repo already implies
(reviewers on `jobs`/`pipeline`/`matching` changes) — an AI reviewer is
a second pair of eyes, not a replacement for one.

## Adding a continuous security agent

Layered defense, cheapest/fastest first:

1. **Static + dependency scanning (done)** — `bandit` + `pip-audit` in
   CI and on a weekly cron, as above. Catches known patterns (SQL
   injection via raw queries, `eval`/`exec`, hardcoded secrets, insecure
   deserialization, etc.) and known-CVE dependencies. Zero LLM cost,
   runs in seconds, deterministic.

2. **Dependabot (done)** — keeps the dependency floor moving forward
   automatically instead of accumulating CVEs silently.

3. **Claude Code's `/security-review` skill, on every PR.** This does
   what static tools can't: reasons about the *diff's* actual behavior
   — e.g. "this new `ApplyToJobView` accepts `job_id` from the URL but
   never checks the job's `status`", or "this Celery task trusts
   `job_id` without validating it belongs to the caller's org" (not
   issues in this codebase today, but the class of thing a pattern
   scanner won't catch and a contextual review will). Wire it the same
   way as the code-review agent above — either it's covered by the
   Claude GitHub App's review, or add a dedicated
   `anthropics/claude-code-action` step running `/security-review`
   instead of `/code-review` on PR events touching `backend/`.

4. **Recurring, whole-repo audits — not just diffs.** A diff-scoped
   review only ever sees what changed *this PR*; it won't notice that
   an old, unrelated endpoint has drifted into being insecure as the
   rest of the system changed around it. Schedule a recurring Claude
   Code session (a cron trigger, or `/loop` with a long interval) that
   runs `/security-review` against the **whole current `main`**, not
   a diff — e.g. weekly, alongside the `security-scan.yml` dependency
   sweep — and has it open an issue (or message you) with anything it
   finds. This is the piece that catches drift the other three layers
   structurally can't.

5. **Treat GDPR/PII handling as a standing review focus**, given this
   product's domain: any change touching `Candidate.resume_text`,
   `Candidate.email`, or anything that could send that data to a new
   destination (a new integration, a new log statement, a new external
   API call) is exactly the class of change worth a mandatory security
   pass — this is also why `core/matching.py` and `ai_service/` are
   built to score resumes with **zero outbound calls to third-party AI
   APIs**: the matching logic runs in-process against your own database,
   which is the same "runs on our own infrastructure" property
   Datacruit's job posting describes for their real AI cluster.

None of this replaces judgment — it's meant to make the cheap, reliable
checks automatic so a human (or a deeper Claude review) can spend their
attention on the 5% of changes that actually need it.
