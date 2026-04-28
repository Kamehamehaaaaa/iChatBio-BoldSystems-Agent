import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.document_retrieval import document_retrieval


@pytest.fixture
def base_state():
    return {
        "session_active": True,
        "process": AsyncMock(),
        "query_id": "ABC123",
        "start": 0,
        "length": 100,
        "user_intent": "occurrence",
    }


# ---------------------------
# 1. Early exit
# ---------------------------
@pytest.mark.asyncio
async def test_session_inactive_returns_early(base_state):
    base_state["session_active"] = False

    result = await document_retrieval(base_state)

    assert result == base_state


# ---------------------------
# 2. Successful retrieval
# ---------------------------
@pytest.mark.asyncio
async def test_successful_document_retrieval(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200

    # simulate streaming JSON lines
    mock_response.iter_lines.return_value = [
        b'{"id": 1}',
        b'{"id": 2}'
    ]

    with patch("requests.get", return_value=mock_response):
        result = await document_retrieval(base_state)

    assert result["documents"] is True
    assert result["records"] == [{"id": 1}, {"id": 2}]

    base_state["process"].log.assert_any_await("Fetching data from Bold systems")
    base_state["process"].create_artifact.assert_awaited_once()


# ---------------------------
# 3. Handles 422 error
# ---------------------------
@pytest.mark.asyncio
async def test_422_error_sets_session_inactive(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.iter_lines.return_value = [
        b'{"error": "bad request"}'
    ]

    with patch("requests.get", return_value=mock_response):
        result = await document_retrieval(base_state)

    assert result["session_active"] is False
    base_state["process"].log.assert_any_await("fetching records failed", data=[{"error": "bad request"}])


# ---------------------------
# 4. URL encoding correctness
# ---------------------------
@pytest.mark.asyncio
async def test_query_id_is_url_encoded(base_state):
    base_state["query_id"] = "ABC 123"  # contains space

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = []

    with patch("requests.get", return_value=mock_response) as mock_get:
        await document_retrieval(base_state)

    called_url = mock_get.call_args[0][0]
    assert "ABC%20123" in called_url


# ---------------------------
# 5. Logs include status code
# ---------------------------
@pytest.mark.asyncio
async def test_logs_status_code(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = []

    with patch("requests.get", return_value=mock_response):
        await document_retrieval(base_state)

    # Check that status code log was called
    calls = base_state["process"].log.await_args_list

    assert any("status code 200" in str(call) for call in calls)


# ---------------------------
# 6. Artifact creation arguments
# ---------------------------
@pytest.mark.asyncio
async def test_artifact_creation_contents(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = []

    with patch("requests.get", return_value=mock_response):
        await document_retrieval(base_state)

    base_state["process"].create_artifact.assert_awaited_once()

    args, kwargs = base_state["process"].create_artifact.await_args

    assert kwargs["mimetype"] == "application/json"
    assert "occurrence" in kwargs["description"]
    assert kwargs["metadata"]["data_source"] == "bold systems"