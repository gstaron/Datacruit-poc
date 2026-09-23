# Datacruit PoC — frontend

An unofficial proof-of-concept web app that recreates the core recruiting
workflow of [datacruit.com](https://www.datacruit.com)'s ATS product: job
postings, AI-assisted resume parsing and candidate matching, a visual
hiring pipeline, interview scheduling, manager evaluations, and hiring
analytics. Not affiliated with Datacruit.

See [`../backend/README.md`](../backend/README.md) for the
Python/Django + FastAPI backend built to match Datacruit's actual
backend job requirements — this frontend was the original standalone
demo and is kept as a full-stack companion.

## Features

- **Job postings** — open roles with must-have / nice-to-have requirements
  (`/jobs`, "+ Post a new job").
- **AI resume parsing & matching** — paste a resume on the apply form and
  the app extracts a skill list and computes an explainable match score
  against the job's requirements (`lib/matching.ts`).
- **Pipeline / Kanban board** — move candidates through
  Applied → Screening → Interview → Offer → Hired / Rejected per job
  (`/jobs/[id]`).
- **Candidate profiles** — resume, AI match breakdown (matched/missing
  skills), interview history, and evaluations (`/candidates/[id]`).
- **Interview scheduling** — schedule interviews with an interviewer,
  type and notes directly from a candidate's profile.
- **Manager portal** — evaluators leave a star rating, hire/no-hire/maybe
  recommendation and comments per candidate.
- **Recruiting dashboard** — open jobs, total candidates, offers extended,
  average time-to-hire, average AI match score, a pipeline funnel chart,
  a candidate-source breakdown, and upcoming interviews (`/`).

## Tech stack

Next.js 14 (App Router) + TypeScript + Tailwind CSS + Recharts. Data is
persisted to a local JSON file (`data/db.json`, gitignored) via Next.js
Server Actions — no external database required. The file is generated
from realistic seed data on first run.

## Getting started

```bash
npm install
npm run dev
```

Then open http://localhost:3000.

## Notes on the "AI" features

The resume parsing and match scoring are a deliberately simple, fully
explainable keyword-overlap algorithm (see `lib/matching.ts`) rather than
a call to a real LLM — it's meant to demonstrate the *product experience*
(automatic parsing, a match score with a matched/missing breakdown) that
Datacruit's AI-powered CV analysis and candidate matching offers, not to
replicate its actual model. The backend's `core/matching.py` is the same
algorithm ported to Python, shared between the Django API and the FastAPI
AI microservice.
