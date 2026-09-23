from ai_service.cache import get_cached_score, set_cached_score


class TestMatchCache:
    def test_round_trips_a_result(self):
        result = {
            "score": 80,
            "matched_must_have": ["Python"],
            "missing_must_have": [],
            "matched_nice_to_have": [],
            "summary": "Strong match.",
        }
        set_cached_score(1, "Python developer.", result)
        assert get_cached_score(1, "Python developer.") == result

    def test_cache_miss_returns_none(self):
        assert get_cached_score(1, "Some resume text nobody cached before.") is None

    def test_different_resume_text_is_a_different_cache_key(self):
        set_cached_score(1, "Python developer.", {"score": 80, "matched_must_have": [], "missing_must_have": [], "matched_nice_to_have": [], "summary": "x"})
        assert get_cached_score(1, "Django developer.") is None
