# CLAUDE.md

Working notes for Claude Code sessions on this repo. See `README.md`,
`backend/README.md`, and `frontend/README.md` for what the project is;
this file is about how to work on it safely.

## Review discipline — read before merging anything nontrivial

Reading a diff line-by-line stops scaling somewhere around a few
thousand lines, but it was never the thing that created confidence —
it was just the cheapest available proxy. These are the permanent
constraints for this repo, written down once so they don't need
repeating every session.

1. **The verification loop is not optional.** Every change goes
   through something that can independently confirm it works:
   `pytest` (100% coverage gate enforced in `backend/pyproject.toml`),
   `bandit`, `pip-audit` — all wired into `backend-ci.yml`. Never call
   code correct here because it "looks right"; the CI gate decides
   that.
2. **Keep increments small.** A PR should have one stated exit
   condition ("this test passes", "this endpoint returns X"). A
   repo-sized change landed in one pass is unreviewable by
   construction, not because anyone failed to look closely enough.
3. **Read these five categories by hand, every time, regardless of
   what CI says** — the ~5% of any diff where a mistake is expensive
   or irreversible:
   - Django migrations (`backend/*/migrations/*.py`)
   - API/schema contracts — DRF serializers (`backend/*/serializers.py`),
     the FastAPI/Pydantic models in `backend/ai_service/main.py`
   - anything implementing auth/permissions (none yet — treat the
     first PR that adds any as high-risk by default)
   - dependency/lockfiles — `backend/requirements*.txt`,
     `frontend/package-lock.json` (a hallucinated or typosquatted
     package name is a real attack vector, not a hypothetical one)
   - config and defaults — `backend/config/settings.py`, `.env.example`,
     `docker-compose.yml` (what happens in production when a variable
     is missing)
4. **Tests are the review surface — but they can lie.** A test can
   mock exactly the thing it's supposed to verify: green CI, zero
   information. Acceptance criteria should come from a human (or be
   copied verbatim from the issue), the implementation from the
   agent. Prefer integration tests against the real dependency over
   unit tests that mock the boundary they're meant to catch bugs at —
   this repo already does that (`ai_service`'s tests run against the
   real Postgres the Django test DB creates, not a mocked engine;
   keep it that way).
5. **Adversarial + security review on the five categories above,
   every time.** Run `/code-review` at `ultra` (an independent pass
   that never saw how the code was written) plus `/security-review`
   before merging anything that touches migrations, API contracts,
   auth, lockfiles, or config defaults. The agent that wrote the code
   is structurally blind to its own assumptions; a second, unrelated
   pass is what catches that class of bug. `.claude/skills/architect/`
   flags when a diff hits one of these categories — treat that flag
   as a requirement, not a suggestion.
6. **Ship it and watch it run.** `docker compose up` locally, the
   `backend-ci.yml` job, and (once the live-demo issue lands) the
   deployed instance are this project's version of "run it for
   real" — behavior is truth, reading code is a guess.

## Explicitly not doing, and why

This is a portfolio-scale project: one contributor, no live traffic.
Staging environments, canary rollouts, and feature flags solve the
problem of de-risking a change against real production traffic — a
problem this project doesn't have yet. Building that infrastructure
here would be cargo-culting process rather than engineering judgment.
If real users or other contributors show up, revisit this section.

Backups are the exception: cheap even at this scale, and worth
actually turning on (see the live-demo issue) rather than deferring
indefinitely.

## Architecture

Diagram of the system and how the proposed review/security/architect/
explainer agents plug into the PR workflow:
https://claude.ai/artifact/94xHdpngVVJAimpmXPBhPi — kept current by
`.claude/skills/architect/`.
