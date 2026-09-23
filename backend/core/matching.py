"""In-house resume/job matching engine.

Deliberately a transparent, explainable keyword-overlap model rather
than a call to a third-party AI API: candidate personal data (resumes)
never leaves our own infrastructure. This module is pure Python with no
Django or Postgres dependency so it can be shared, unchanged, between
the Django REST API (``pipeline`` app) and the FastAPI AI inference
microservice (``ai_service``) that would run on Datacruit's own AI
cluster.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_STOPWORDS = frozenset(
    {
        "the", "and", "for", "with", "a", "an", "of", "to", "in", "on", "or",
        "is", "are", "as", "at", "by", "be", "this", "that", "will", "you",
        "we", "our", "have", "has", "years", "year", "experience", "strong",
        "knowledge", "ability", "working", "skills", "but", "no",
    }
)

_NON_TOKEN_CHARS = re.compile(r"[^a-z0-9+#.\s]")
_TRAILING_DOTS = re.compile(r"\.+$")


def tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, and split ``text`` into keyword tokens.

    Periods are kept mid-token (so "Node.js" and "C#"-style names survive)
    but a lone trailing period — the end of a sentence — is stripped so
    "communication." matches the skill "communication".
    """
    cleaned = _NON_TOKEN_CHARS.sub(" ", text.lower())
    tokens = []
    for word in cleaned.split():
        word = _TRAILING_DOTS.sub("", word)
        if len(word) > 1 and word not in _STOPWORDS:
            tokens.append(word)
    return tokens


def _skill_tokens_present(skill: str, haystack: set[str]) -> bool:
    skill_tokens = tokenize(skill)
    return bool(skill_tokens) and all(t in haystack for t in skill_tokens)


def extract_skills(text: str, vocabulary: list[str]) -> list[str]:
    """Return the subset of ``vocabulary`` whose keywords all appear in ``text``."""
    haystack = set(tokenize(text))
    return [skill for skill in vocabulary if _skill_tokens_present(skill, haystack)]


@dataclass(frozen=True)
class MatchBreakdown:
    score: int
    matched_must_have: list[str] = field(default_factory=list)
    missing_must_have: list[str] = field(default_factory=list)
    matched_nice_to_have: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "matched_must_have": self.matched_must_have,
            "missing_must_have": self.missing_must_have,
            "matched_nice_to_have": self.matched_nice_to_have,
            "summary": self.summary,
        }


_MUST_HAVE_WEIGHT = 0.75
_NICE_TO_HAVE_WEIGHT = 0.25


def _summary_for(score: int) -> str:
    if score >= 85:
        return "Excellent match — covers nearly all requirements."
    if score >= 65:
        return "Strong match — meets most must-have requirements."
    if score >= 40:
        return "Partial match — some key requirements are missing."
    return "Weak match — resume covers few of the job's requirements."


def score_candidate(
    resume_text: str,
    skills: list[str],
    must_have: list[str],
    nice_to_have: list[str],
) -> MatchBreakdown:
    """Score a candidate's resume against a job's requirements.

    Weighted keyword overlap: must-have requirements count for 75% of the
    score, nice-to-have for 25%. A job with no requirements in a category
    trivially scores 100% on that category (nothing to be missing).
    """
    haystack = set(tokenize(resume_text))
    for skill in skills:
        haystack.update(tokenize(skill))

    matched_must_have = [s for s in must_have if _skill_tokens_present(s, haystack)]
    missing_must_have = [s for s in must_have if s not in matched_must_have]
    matched_nice_to_have = [s for s in nice_to_have if _skill_tokens_present(s, haystack)]

    must_have_score = 1.0 if not must_have else len(matched_must_have) / len(must_have)
    nice_to_have_score = 1.0 if not nice_to_have else len(matched_nice_to_have) / len(nice_to_have)

    raw_score = must_have_score * _MUST_HAVE_WEIGHT + nice_to_have_score * _NICE_TO_HAVE_WEIGHT
    score = round(raw_score * 100)

    return MatchBreakdown(
        score=score,
        matched_must_have=matched_must_have,
        missing_must_have=missing_must_have,
        matched_nice_to_have=matched_nice_to_have,
        summary=_summary_for(score),
    )
