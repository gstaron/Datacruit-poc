# Datacruit PoC — backend

A Django REST Framework API + FastAPI AI microservice, built test-first,
to match the actual stack in Datacruit's Backend Python Developer job
posting: **Python 3, Django, PostgreSQL, custom REST APIs**, with the
listed nice-to-haves — **FastAPI, SQLAlchemy, Redis** — used for a
real, separate AI-matching service rather than bolted on for show.

It implements the same recruiting-ATS domain as [`../frontend`](../frontend):
jobs, candidates, a pipeline (kanban stages), interviews, evaluations,
and an explainable AI match-scoring engine — this time as a proper
REST API with a real Postgres database, 100% test coverage, and CI.

## Why this shape

The job posting specifically calls out building an **in-house AI
cluster** so candidate personal data never reaches a third-party AI
API. `core/matching.py` is a deliberately transparent, explainable
keyword-overlap scoring engine with zero external network calls — it's
shared, unchanged, between the Django app and the FastAPI service, so
"the same AI logic runs identically on our own infrastructure whether
it's called synchronously from the API or from the standalone inference
service" is a real, working property of this codebase, not a slide.

## Architecture

```
backend/
├── config/          Django project settings, URL root, Celery app
├── core/            Shared matching engine (pure Python, no framework
│                    deps) + an ad-hoc /api/matching/score/ endpoint
├── jobs/            Job postings (DRF ModelViewSet)
├── candidates/       Candidate records (DRF ModelViewSet)
├── pipeline/         Application (candidate × job, pipeline stage,
│                    match score), the /apply/ endpoint, the
│                    move-stage action, and the Celery recompute task
├── interviews/       Interview scheduling (auto-advances a fresh
│                    application to "screening" on first interview)
├── evaluations/      Manager feedback / hire recommendations
├── analytics/        /api/dashboard/ aggregate metrics
└── ai_service/       FastAPI + SQLAlchemy AI matching microservice —
                     a separate process, reads Job requirements from
                     the same Postgres DB, caches results in Redis
```

Each Django app owns one model concept; `pipeline` is the one exception
that's allowed to depend on `jobs` and `candidates` (via FK) since an
Application *is* the relationship between them. `ai_service` never
imports Django — it only imports the framework-agnostic `core.matching`
module, and reaches Postgres through its own SQLAlchemy engine.

## Tech stack

| Requirement (from the job posting) | Used here |
|---|---|
| Python 3, Django | Django 5.2 LTS |
| PostgreSQL | primary datastore (`psycopg2`) |
| Custom REST APIs in Python | Django REST Framework |
| FastAPI (nice-to-have) | `ai_service/` — standalone matching microservice |
| SQLAlchemy (nice-to-have) | `ai_service/db.py` reads Postgres directly |
| Redis (nice-to-have) | Celery broker + Django cache + AI service's own result cache |
| In-house AI, no external APIs | `core/matching.py` — pure-Python, in-process scoring |

## Getting started

### Option A — docker-compose (Postgres + Redis + Django + Celery + FastAPI)

```bash
docker compose up --build
```

- Django API: http://localhost:8000/api/
- FastAPI AI service: http://localhost:8001/docs
- Django admin: http://localhost:8000/admin/ (create a superuser first:
  `docker compose exec web python manage.py createsuperuser`)

### Option B — native (what this was actually developed and tested against)

Requires local PostgreSQL and Redis running.

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env   # adjust DATABASE_URL/REDIS_URL if needed
createdb datacruit

python manage.py migrate
python manage.py runserver             # Django API on :8000

# in a second shell, for the AI microservice:
uvicorn ai_service.main:app --reload --port 8001

# in a third shell, for async match recomputation:
celery -A config worker --loglevel=info
```

## Running the tests and coverage report

This was built test-first (TDD): the test files for `core.matching`,
each model, and each API endpoint were written before — or immediately
alongside — the implementation, and several of them caught real bugs
during development (a tokenizer edge case, a stale-cache bug in the
`move-stage` action, and an uncaught `IntegrityError` on duplicate
applications) before any of this shipped.

```bash
cd backend
source .venv/bin/activate
export DATABASE_URL=postgres://postgres:postgres@localhost:5432/datacruit
pytest
```

`pytest.ini` already runs coverage by default
(`--cov --cov-report=term-missing --cov-report=html`), and
`pyproject.toml` sets `fail_under = 100` — the suite fails the build if
coverage drops below 100%. An HTML report is written to
`backend/htmlcov/index.html`.

**Actual result from this codebase:**

```
96 passed
TOTAL coverage: 100% (statements and branches)
```

Coverage excludes `migrations/`, `manage.py`, and the WSGI/ASGI entry
points (see `[tool.coverage.run] omit` in `pyproject.toml`) — those are
Django-generated/boilerplate, not code with meaningful branches to test.

## API overview

All endpoints are under `/api/`.

| Endpoint | Purpose |
|---|---|
| `GET/POST /jobs/`, `/jobs/{id}/` | Job postings CRUD |
| `POST /jobs/{id}/apply/` | Apply to a job — parses the resume, computes an AI match score, creates the Candidate + Application |
| `GET/POST /candidates/` | Candidate records |
| `GET /applications/?job=&stage=` | Pipeline / kanban data |
| `POST /applications/{id}/move-stage/` | Move a candidate through the pipeline |
| `GET/POST /interviews/` | Scheduling (auto-advances stage on first interview) |
| `GET/POST /evaluations/` | Manager feedback |
| `GET /dashboard/` | Aggregate metrics: funnel, source breakdown, avg. time-to-hire, avg. match score, upcoming interviews |
| `POST /matching/score/` | Ad-hoc AI match scoring (by `job_id` or explicit `must_have`/`nice_to_have`) |

FastAPI service (`ai_service/`, separate process, port 8001):

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness check |
| `POST /jobs/{job_id}/match` | Score a resume against a job read live from Postgres, cached in Redis |

## CI, code review and security

See [`../SECURITY.md`](../SECURITY.md) for the full picture, including
how to layer a Claude-powered code-review and security-review agent on
top of this. In short, already wired up in `.github/workflows/`:

- **`backend-ci.yml`** — tests (100% coverage gate), `bandit`,
  `pip-audit` on every push/PR.
- **`security-scan.yml`** — the same scanners on a weekly schedule, so
  newly disclosed CVEs in pinned dependencies get caught even without a
  code change.
- **`dependabot.yml`** — automated weekly dependency-update PRs.
