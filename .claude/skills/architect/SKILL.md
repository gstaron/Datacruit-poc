---
name: architect
description: Checks the repo for architecture drift (real structure vs what the READMEs/diagram claim) and flags any diff that touches a high-risk surface (migrations, API contracts, auth, lockfiles, config defaults) as needing adversarial + security review before merge. Invoke as /architect, or run it before merging any nontrivial PR.
---

# Architect

Two jobs, both about keeping claims this repo makes about itself honest.

## 1. Drift check

Compare what's actually in the repo against what the docs claim:

- `backend/README.md`'s architecture tree (the `backend/` directory
  listing under "Architecture") vs the real list of Django apps and
  top-level services — flag any app, FastAPI route file, or service
  not mentioned there.
- The one-exception rule in `backend/README.md`: only `pipeline/` may
  depend on `jobs/` and `candidates/` via FK. Grep
  `backend/*/models.py` for cross-app `ForeignKey`/`OneToOneField`
  references and flag any other app doing the same.
- `docker-compose.yml` services vs what `backend/README.md`'s
  "Option A — docker-compose" section describes — flag services added
  or removed that aren't documented there.
- The architecture diagram
  (https://claude.ai/artifact/94xHdpngVVJAimpmXPBhPi) vs the above —
  note when it's gone stale. Don't republish it yourself unless asked;
  report drift, don't silently fix it.

## 2. High-risk surface flagging

For the current diff (uncommitted changes, or a named branch/PR),
check whether it touches any of:

- Django migrations (`backend/*/migrations/*.py`)
- API/schema contracts — DRF serializers (`backend/*/serializers.py`),
  the FastAPI/Pydantic models in `backend/ai_service/main.py`
- anything implementing auth/permissions
- dependency/lockfiles (`backend/requirements*.txt`,
  `frontend/package-lock.json`)
- config/defaults (`backend/config/settings.py`, `.env.example`,
  `docker-compose.yml`)

If it does: say so explicitly and name `/code-review` at `ultra` plus
`/security-review` as required before merge (per `CLAUDE.md`'s review
discipline). Don't run those yourself as part of this skill — this
skill only decides whether they're required, it isn't a substitute for
them.

## Output

A short report, not a wall of text:

- **Drift found:** each item, or "none".
- **High-risk surfaces touched:** each file/category, or "none".
- **One line:** clear to merge on the architecture/risk axis as-is, or
  blocked on the reviews above.

## Out of scope

Don't edit the README, the diagram, or `CLAUDE.md` yourself — report
drift and let a human (or a follow-up instruction) decide what to
update. Don't run `/code-review` or `/security-review` automatically —
require them, don't substitute for them.
