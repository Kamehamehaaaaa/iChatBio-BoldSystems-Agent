import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.summary_decision import summary_decision


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

    result = await summary_decision(base_state)

    assert result == base_state


# ---------------------------
# 2. Session is always deactivated
# ---------------------------
@pytest.mark.asyncio
async def test_session_set_inactive(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response):
        result = await summary_decision(base_state)

    assert result["session_active"] is False


# ---------------------------
# 3. Successful summary → artifact created
# ---------------------------
@pytest.mark.asyncio
async def test_success_creates_artifact(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "summary"}

    with patch("requests.get", return_value=mock_response):
        await summary_decision(base_state)

    base_state["process"].create_artifact.assert_awaited_once()


# ---------------------------
# 4. Handles 422 error (no artifact)
# ---------------------------
@pytest.mark.asyncio
async def test_422_error_logs_and_skips_artifact(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.json.return_value = {"error": "bad request"}

    with patch("requests.get", return_value=mock_response):
        result = await summary_decision(base_state)

    assert result["session_active"] is False

    base_state["process"].log.assert_any_await(
        "Error while generating summary data.", data={"error": "bad request"}
    )

    base_state["process"].create_artifact.assert_not_awaited()


# ---------------------------
# 5. Query concatenation (no separators)
# ---------------------------
@pytest.mark.asyncio
async def test_triplets_concatenated_without_separator(base_state):
    base_state["valid_triplets"] = ["a", "b", "c"]

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response) as mock_get:
        await summary_decision(base_state)

    called_url = mock_get.call_args[0][0]

    # note: no semicolons
    assert "abc" in called_url


# ---------------------------
# 6. URL encoding
# ---------------------------
@pytest.mark.asyncio
async def test_query_is_url_encoded(base_state):
    base_state["valid_triplets"] = ["fish species"]  # space

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response) as mock_get:
        await summary_decision(base_state)

    called_url = mock_get.call_args[0][0]

    assert "fish%20species" in called_url


# ---------------------------
# 7. Logs status code
# ---------------------------
@pytest.mark.asyncio
async def test_logs_status_code(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response):
        await summary_decision(base_state)

    calls = base_state["process"].log.await_args_list

    assert any("code: 200" in str(call) for call in calls)


# ---------------------------
# 8. Artifact metadata correctness
# ---------------------------
@pytest.mark.asyncio
async def test_artifact_metadata(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response):
        await summary_decision(base_state)

    args, kwargs = base_state["process"].create_artifact.await_args

    assert kwargs["mimetype"] == "application/json"
    assert kwargs["description"] == "summary generated"
    assert kwargs["metadata"]["data_source"] == "bold systems"