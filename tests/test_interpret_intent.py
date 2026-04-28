# import pytest
# from unittest.mock import AsyncMock, MagicMock

# from tools.interpret_intent import interpret_intent
# from state import BoldAgentState


# @pytest.fixture
# def base_state():
#     return {
#         "session_active": True,
#         "context": MagicMock(),
#         "process": AsyncMock(),
#         "user_query": "test query",
#     }


# @pytest.mark.asyncio
# async def test_session_inactive_returns_early(base_state):
#     base_state["session_active"] = False

#     result = await interpret_intent(base_state)

#     assert result == base_state


# @pytest.mark.asyncio
# async def test_sets_intent_and_terms(base_state):
#     mock_response = MagicMock()
#     mock_response.model_dump.return_value = {
#         "user_intent": "occurrence",
#         "terms": [],
#         "clarification_needed": False,
#         "query_needs": ["taxonomy"]
#     }

#     mock_client = MagicMock()
#     mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

#     base_state["context"].instructor_client = mock_client

#     result = await interpret_intent(base_state)

#     assert result["user_intent"] == "occurrence"
#     assert result["clarification_needed"] is False
#     assert result["query_needs"] == ["taxonomy"]


# @pytest.mark.asyncio
# async def test_unresolved_term_no_match(monkeypatch, base_state):
#     mock_response = MagicMock()
#     mock_response.model_dump.return_value = {
#         "terms": [
#             {"value": "abc", "scope": "unresolved"}
#         ]
#     }

#     mock_client = MagicMock()
#     mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

#     base_state["context"].instructor_client = mock_client

#     async def mock_resolver(term):
#         return 0, []

#     monkeypatch.setattr(
#         "utils.partial_term_resolver",
#         mock_resolver
#     )

#     result = await interpret_intent(base_state)

#     assert result["session_active"] is False


# @pytest.mark.asyncio
# async def test_unresolved_term_with_matches(monkeypatch, base_state):
#     mock_response = MagicMock()
#     mock_response.model_dump.return_value = {
#         "terms": [
#             {"value": "abc", "scope": "unresolved"}
#         ]
#     }

#     mock_client = MagicMock()
#     mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

#     base_state["context"].instructor_client = mock_client

#     async def mock_resolver(term):
#         return 1, ["match1", "match2"]

#     monkeypatch.setattr(
#         "utils.partial_term_resolver",
#         mock_resolver
#     )

#     result = await interpret_intent(base_state)

#     assert result["session_active"] is False


# @pytest.mark.asyncio
# async def test_clarification_flag(monkeypatch, base_state):
#     mock_response = MagicMock()
#     mock_response.model_dump.return_value = {
#         "clarification_needed": True,
#         "terms": []
#     }

#     mock_client = MagicMock()
#     mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

#     base_state["context"].instructor_client = mock_client

#     result = await interpret_intent(base_state)

#     assert result["clarification_needed"] is True

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.interpret_intent import interpret_intent


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
async def test_uses_existing_instructor_client(base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {}

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    await interpret_intent(base_state)

    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_adds_client_if_missing(base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {}

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("utils.add_client", return_value=mock_client):
        base_state["context"].instructor_client = None

        await interpret_intent(base_state)

        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_sets_all_state_fields(base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "user_intent": "occurrence",
        "terms": [{"value": "fish"}],
        "clarification_needed": True,
        "post_filters": {"year": 2020},
        "start": 10,
        "length": 50,
        "query_needs": ["taxonomy", "location"],
    }

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    result = await interpret_intent(base_state)

    assert result["user_intent"] == "occurrence"
    assert result["extracted_terms"] == [{"value": "fish"}]
    assert result["clarification_needed"] is True
    assert result["post_filters"] == {"year": 2020}
    assert result["start"] == 10
    assert result["length"] == 50
    assert result["query_needs"] == ["taxonomy", "location"]


@pytest.mark.asyncio
async def test_defaults_when_fields_missing(base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {}

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    result = await interpret_intent(base_state)

    assert result["user_intent"] == ""
    assert result["extracted_terms"] == []
    assert result["clarification_needed"] is False
    assert result["post_filters"] is None
    assert result["start"] == 0
    assert result["length"] == 1000
    assert result["query_needs"] == []


@pytest.mark.asyncio
async def test_logs_params(base_state):
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {"user_intent": "test"}

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    base_state["context"].instructor_client = mock_client

    await interpret_intent(base_state)

    base_state["process"].log.assert_awaited_once()