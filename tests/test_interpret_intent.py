import pytest
from unittest.mock import AsyncMock, MagicMock

from tools.interpret_intent import interpret_intent
from state import BoldAgentState


@pytest.fixture
def base_state():
    return {
        "session_active": True,
        "context": MagicMock(),
        "process": AsyncMock(),
        "user_query": "test query",
    }


@pytest.mark.asyncio
async def test_session_inactive_returns_early(base_state):
    base_state["session_active"] = False

    result = await interpret_intent(base_state)

    assert result == base_state


@pytest.mark.asyncio
async def test_sets_intent_and_terms(base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "user_intent": "occurrence",
        "terms": [],
        "clarification_needed": False,
        "query_needs": ["taxonomy"]
    }

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    result = await interpret_intent(base_state)

    assert result["user_intent"] == "occurrence"
    assert result["clarification_needed"] is False
    assert result["query_needs"] == ["taxonomy"]


@pytest.mark.asyncio
async def test_unresolved_term_no_match(monkeypatch, base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "terms": [
            {"value": "abc", "scope": "unresolved"}
        ]
    }

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    async def mock_resolver(term):
        return 0, []

    monkeypatch.setattr(
        "utils.partial_term_resolver",
        mock_resolver
    )

    result = await interpret_intent(base_state)

    assert result["session_active"] is False


@pytest.mark.asyncio
async def test_unresolved_term_with_matches(monkeypatch, base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "terms": [
            {"value": "abc", "scope": "unresolved"}
        ]
    }

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    async def mock_resolver(term):
        return 1, ["match1", "match2"]

    monkeypatch.setattr(
        "utils.partial_term_resolver",
        mock_resolver
    )

    result = await interpret_intent(base_state)

    assert result["session_active"] is False


@pytest.mark.asyncio
async def test_clarification_flag(monkeypatch, base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "clarification_needed": True,
        "terms": []
    }

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    result = await interpret_intent(base_state)

    assert result["clarification_needed"] is True