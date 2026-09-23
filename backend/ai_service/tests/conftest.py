import pytest
from django.db import connection

import ai_service.cache as cache_module
import ai_service.db as db_module


@pytest.fixture(autouse=True)
def _use_django_test_database(monkeypatch):
    """Point the FastAPI service's SQLAlchemy engine at whichever Postgres
    database Django's test runner is currently using (pytest-django swaps
    in a dedicated test database), so rows created via the Django ORM in
    a test are visible to this service's separate SQLAlchemy connection.
    """
    settings_dict = connection.settings_dict
    url = (
        f"postgresql://{settings_dict['USER']}:{settings_dict['PASSWORD']}"
        f"@{settings_dict['HOST'] or 'localhost'}:{settings_dict['PORT'] or 5432}/{settings_dict['NAME']}"
    )
    monkeypatch.setenv("DATABASE_URL", url)
    db_module.get_engine.cache_clear()
    yield
    db_module.get_engine.cache_clear()


@pytest.fixture(autouse=True)
def _clean_match_cache():
    client = cache_module.get_client()
    for key in client.scan_iter("ai-match:*"):
        client.delete(key)
    yield
    for key in client.scan_iter("ai-match:*"):
        client.delete(key)
