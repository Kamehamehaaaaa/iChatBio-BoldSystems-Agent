import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.query_creation import query_creation


@pytest.fixture
def base_state():
    return {
        "session_active": True,
        "process": AsyncMock(),
        "valid_triplets": ["tax:fish", "loc:canada"],
    }


# ---------------------------
# 1. Early exit
# ---------------------------
@pytest.mark.asyncio
async def test_session_inactive_returns_early(base_state):
    base_state["session_active"] = False

    result = await query_creation(base_state)

    assert result == base_state


# ---------------------------
# 2. Successful query creation
# ---------------------------
@pytest.mark.asyncio
async def test_successful_query_creation(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"query_id": "Q123"}

    with patch("requests.get", return_value=mock_response):
        result = await query_creation(base_state)

    assert result["query_id"] == "Q123"
    base_state["process"].log.assert_any_await("Preprocessing query")


# ---------------------------
# 3. Handles 422 error
# ---------------------------
@pytest.mark.asyncio
async def test_422_error_sets_session_inactive(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.json.return_value = {"error": "invalid query"}

    with patch("requests.get", return_value=mock_response):
        result = await query_creation(base_state)

    assert result["session_active"] is False
    base_state["process"].log.assert_any_await(
        "generating QueryId failed", data={"error": "invalid query"}
    )


# ---------------------------
# 4. Query string construction
# ---------------------------
@pytest.mark.asyncio
async def test_query_string_concatenation(base_state):
    base_state["valid_triplets"] = ["a", "b", "c"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"query_id": "Q1"}

    with patch("requests.get", return_value=mock_response) as mock_get:
        await query_creation(base_state)

    called_url = mock_get.call_args[0][0]

    assert "a%3Bb%3Bc" in called_url


# ---------------------------
# 5. URL encoding
# ---------------------------
@pytest.mark.asyncio
async def test_query_is_url_encoded(base_state):
    base_state["valid_triplets"] = ["tax:fish species"]  # space

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"query_id": "Q1"}

    with patch("requests.get", return_value=mock_response) as mock_get:
        await query_creation(base_state)

    called_url = mock_get.call_args[0][0]

    assert "fish%20species" in called_url


# ---------------------------
# 6. Missing query_id defaults to empty string
# ---------------------------
@pytest.mark.asyncio
async def test_missing_query_id_defaults_empty(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}  # no query_id

    with patch("requests.get", return_value=mock_response):
        result = await query_creation(base_state)

    assert result["query_id"] == ""


# ---------------------------
# 7. Logs status code
# ---------------------------
@pytest.mark.asyncio
async def test_logs_status_code(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"query_id": "Q1"}

    with patch("requests.get", return_value=mock_response):
        await query_creation(base_state)

    calls = base_state["process"].log.await_args_list

    assert any("returned: 200" in str(call) for call in calls)