# Datacruit PoC

An unofficial proof-of-concept recruiting/ATS product, built as a
portfolio piece for a **Backend Python Developer** application at
[Datacruit](https://www.datacruit.com) — a Czech HR-tech startup whose
own ATS is used by companies across 10 European countries. Not
affiliated with Datacruit.

Two parts, same domain (jobs, candidates, a hiring pipeline, interview
scheduling, manager evaluations, and explainable AI-assisted resume
matching that runs entirely in-process — no third-party AI API calls):

- **[`backend/`](backend/README.md)** — the primary deliverable: Django
  REST Framework + PostgreSQL, with a FastAPI + SQLAlchemy AI matching
  microservice and Redis (Celery broker, caching), matching the exact
  stack in Datacruit's job posting. Built test-first, **100% test
  coverage enforced in CI**.
- **[`frontend/`](frontend/README.md)** — a Next.js/TypeScript UI over
  the same domain, the original standalone demo.

See [`SECURITY.md`](SECURITY.md) for the CI security/code-review setup
and how to extend it with Claude-powered review agents.

## Quick start

```bash
# Backend API (Django + DRF + Postgres + Redis + FastAPI AI service)
docker compose up --build
# → http://localhost:8000/api/  and  http://localhost:8001/docs

# Frontend demo
cd frontend && npm install && npm run dev
# → http://localhost:3000
```

Full setup, test/coverage commands, and API reference:
[`backend/README.md`](backend/README.md).
