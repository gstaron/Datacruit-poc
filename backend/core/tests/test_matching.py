"""Unit tests for the in-house resume/job matching engine.

Written before core/matching.py (TDD): these define the contract the
implementation has to satisfy. The engine is deliberately a transparent,
explainable keyword-overlap model that runs entirely in-process — no
external AI API calls, mirroring Datacruit's own in-house AI cluster
approach to handling candidate personal data.
"""

from core.matching import MatchBreakdown, extract_skills, score_candidate, tokenize


class TestTokenize:
    def test_lowercases_and_splits_on_whitespace(self):
        assert tokenize("React TypeScript") == ["react", "typescript"]

    def test_strips_punctuation_around_words(self):
        assert tokenize("Skilled in Python, Django, and PostgreSQL.") == [
            "skilled",
            "python",
            "django",
            "postgresql",
        ]

    def test_strips_trailing_sentence_period_without_breaking_dotted_tokens(self):
        # Regression guard: a naive "strip all dots" tokenizer would also
        # mangle "Node.js" or "C#" style compound skill names.
        tokens = tokenize("Experienced with Node.js and C#.")
        assert "node.js" in tokens
        assert "c#" in tokens
        assert "communication." not in tokenize("Strong communication.")
        assert "communication" in tokenize("Strong communication.")

    def test_filters_out_stopwords_and_single_characters(self):
        tokens = tokenize("I have 5 years of experience with a strong ability")
        assert "have" not in tokens
        assert "experience" not in tokens
        assert "a" not in tokens

    def test_empty_string_returns_no_tokens(self):
        assert tokenize("") == []


class TestExtractSkills:
    def test_finds_single_word_skills_present_in_text(self):
        found = extract_skills("I use Python and Django daily.", ["Python", "Django", "Redis"])
        assert set(found) == {"Python", "Django"}

    def test_finds_multi_word_skills_only_when_all_tokens_present(self):
        found = extract_skills(
            "Built REST APIs with Django REST Framework.",
            ["Django REST Framework", "REST APIs", "GraphQL"],
        )
        assert set(found) == {"Django REST Framework", "REST APIs"}

    def test_is_case_insensitive(self):
        found = extract_skills("python and DJANGO experience", ["Python", "Django"])
        assert set(found) == {"Python", "Django"}

    def test_returns_empty_list_for_no_matches(self):
        assert extract_skills("Experienced painter and sculptor.", ["Python", "Django"]) == []


class TestScoreCandidate:
    def test_perfect_match_scores_100(self):
        result = score_candidate(
            resume_text="Expert in Python, Django and PostgreSQL, with FastAPI and Redis on the side.",
            skills=[],
            must_have=["Python", "Django", "PostgreSQL"],
            nice_to_have=["FastAPI", "Redis"],
        )
        assert result.score == 100
        assert result.matched_must_have == ["Python", "Django", "PostgreSQL"]
        assert result.missing_must_have == []
        assert set(result.matched_nice_to_have) == {"FastAPI", "Redis"}

    def test_partial_must_have_match_is_weighted_more_than_nice_to_have(self):
        # 2/3 must-have (weight 0.75) + 0/2 nice-to-have (weight 0.25)
        # => 0.6667 * 0.75 = 50% rounded
        result = score_candidate(
            resume_text="Python and Django developer.",
            skills=[],
            must_have=["Python", "Django", "PostgreSQL"],
            nice_to_have=["FastAPI", "Redis"],
        )
        assert result.score == 50
        assert result.missing_must_have == ["PostgreSQL"]

    def test_no_overlap_scores_zero(self):
        result = score_candidate(
            resume_text="Experienced oil painter and muralist.",
            skills=[],
            must_have=["Python", "Django"],
            nice_to_have=["Redis"],
        )
        assert result.score == 0
        assert result.missing_must_have == ["Python", "Django"]

    def test_no_requirements_scores_100_by_convention(self):
        result = score_candidate(
            resume_text="Anything at all.",
            skills=[],
            must_have=[],
            nice_to_have=[],
        )
        assert result.score == 100

    def test_negated_mentions_still_count_as_keyword_matches(self):
        # Documents a known, intentional limitation of pure keyword
        # matching: "no Django experience" still contains the token
        # "django". This is why resumes should be written positively —
        # a real NLP/LLM-based model (see ai_service) can do better.
        result = score_candidate(
            resume_text="No Django experience, but eager to learn.",
            skills=[],
            must_have=["Django"],
            nice_to_have=[],
        )
        assert result.score == 100

    def test_summary_bands(self):
        excellent = score_candidate("Python Django PostgreSQL", [], ["Python", "Django", "PostgreSQL"], [])
        assert "Excellent" in excellent.summary

        weak = score_candidate("Oil painting", [], ["Python", "Django", "PostgreSQL", "Redis"], [])
        assert "Weak" in weak.summary

    def test_skills_list_supplements_resume_text(self):
        # A candidate's separately-tracked skill list (e.g. from a prior
        # parse) should count even if the raw resume text alone wouldn't
        # mention a requirement by that exact wording.
        result = score_candidate(
            resume_text="Experienced software engineer.",
            skills=["Python", "Django"],
            must_have=["Python", "Django"],
            nice_to_have=[],
        )
        assert result.score == 100
        assert result.matched_must_have == ["Python", "Django"]

    def test_result_is_a_match_breakdown_dataclass(self):
        result = score_candidate("Python", [], ["Python"], [])
        assert isinstance(result, MatchBreakdown)
        # dataclasses are trivially serializable to dict for API responses
        assert result.to_dict()["score"] == 100
