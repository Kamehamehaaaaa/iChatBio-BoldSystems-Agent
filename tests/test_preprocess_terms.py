import pytest
from unittest.mock import AsyncMock, MagicMock

from tools.preprocess_terms import preprocess_terms, populate_with_resolver


@pytest.fixture
def base_state():
    return {
        "session_active": True,
        "process": AsyncMock(),
        "extracted_terms": [{"scope": "tax", "value": "abc"}],
        "valid_triplets": []
    }

@pytest.mark.asyncio
async def test_populate_with_resolver_success(monkeypatch):
    async def mock_resolver(term):
        return 1, [{"scope": "tax", "value": "abc"}]

    monkeypatch.setattr(
        "tools.preprocess_terms.partial_term_resolver",
        mock_resolver
    )

    result, _ = await populate_with_resolver({"scope": "tax", "value": "abc"})

    assert result is True


@pytest.mark.asyncio
async def test_populate_with_resolver_failure(monkeypatch):
    async def mock_resolver(term):
        return 0, []

    monkeypatch.setattr(
        "tools.preprocess_terms.partial_term_resolver",
        mock_resolver
    )

    res, _ = await populate_with_resolver({'value': 'abc'})

    assert res is False

@pytest.mark.asyncio
async def test_preprocess_success(monkeypatch, base_state):

    # mock token conversion
    monkeypatch.setattr(
        "utils.params_to_token",
        lambda x: "test"
    )

    # mock resolver
    async def mock_resolver(term):
        return 1, [{"scope": "tax"}]

    monkeypatch.setattr(
        "tools.preprocess_terms.populate_with_resolver",
        AsyncMock(return_value=True)
    )

    # mock requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "successful_terms": [
            {"matched": "tax:abc;extra"}
        ],
        "failed_terms": []
    }

    monkeypatch.setattr(
        "tools.preprocess_terms.requests.get",
        lambda *args, **kwargs: mock_response
    )

    result = await preprocess_terms(base_state)

    assert result["session_active"] is True
    assert "tax:abc" in result["valid_triplets"]

@pytest.mark.asyncio
async def test_preprocess_invalid_triplets(monkeypatch, base_state):

    monkeypatch.setattr(
        "utils.params_to_token",
        lambda x: "test"
    )

    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.json.return_value = {}

    monkeypatch.setattr(
        "tools.preprocess_terms.requests.get",
        lambda *args, **kwargs: mock_response
    )

    result = await preprocess_terms(base_state)

    assert result["session_active"] is False

@pytest.mark.asyncio
async def test_preprocess_resolver_fail(monkeypatch, base_state):

    monkeypatch.setattr(
        "utils.params_to_token",
        lambda x: "test"
    )

    monkeypatch.setattr(
        "tools.preprocess_terms.populate_with_resolver",
        AsyncMock(return_value=(False,{}))
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "successful_terms": [
            {"matched": "tax:abc;extra"}
        ]
    }

    monkeypatch.setattr(
        "tools.preprocess_terms.requests.get",
        lambda *args, **kwargs: mock_response
    )

    result = await preprocess_terms(base_state)

    assert result["session_active"] is False

@pytest.mark.asyncio
async def test_preprocess_session_inactive(base_state):
    base_state["session_active"] = False

    result = await preprocess_terms(base_state)

    assert result == base_state