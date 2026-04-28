import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.generate_map import generate_map


@pytest.fixture
def base_state():
    return {
        "session_active": True,
        "process": AsyncMock(),
        "query_id": "ABC123",
        "user_intent": "occurrence",
    }


# ---------------------------
# 1. Early exit
# ---------------------------
@pytest.mark.asyncio
async def test_session_inactive_returns_early(base_state):
    base_state["session_active"] = False

    result = await generate_map(base_state)

    assert result == base_state


# ---------------------------
# 2. Successful map generation
# ---------------------------
@pytest.mark.asyncio
async def test_successful_map_generation(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"map": "data"}

    with patch("requests.get", return_value=mock_response):
        result = await generate_map(base_state)

    assert result == {"geomap": True}

    base_state["process"].log.assert_any_await(
        "Generating geographic map for collection records from Bold systems"
    )
    base_state["process"].create_artifact.assert_awaited_once()


# ---------------------------
# 3. Handles 422 error (JSON response)
# ---------------------------
@pytest.mark.asyncio
async def test_422_error_with_json_response(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"error": "bad request"}

    with patch("requests.get", return_value=mock_response):
        result = await generate_map(base_state)

    # NOTE: session_active is NOT changed in this function
    assert result == base_state

    base_state["process"].log.assert_any_await(
        "generate map failed",
        data={"error": "bad request"},
    )

    base_state["process"].create_artifact.assert_not_awaited()


# ---------------------------
# 4. 422 error WITHOUT JSON content-type (edge case bug)
# ---------------------------
@pytest.mark.asyncio
async def test_422_error_without_json_content_type(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 422
    mock_response.headers = {"Content-Type": "text/html"}  # no JSON

    with patch("requests.get", return_value=mock_response):
        # This will raise because response_json is undefined
        with pytest.raises(UnboundLocalError):
            await generate_map(base_state)


# ---------------------------
# 5. URL encoding correctness
# ---------------------------
@pytest.mark.asyncio
async def test_query_id_is_url_encoded(base_state):
    base_state["query_id"] = "ABC 123"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response) as mock_get:
        await generate_map(base_state)

    called_url = mock_get.call_args[0][0]

    assert "ABC%20123" in called_url


# ---------------------------
# 6. Logs include status code
# ---------------------------
@pytest.mark.asyncio
async def test_logs_status_code(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response):
        await generate_map(base_state)

    calls = base_state["process"].log.await_args_list

    assert any("status code 200" in str(call) for call in calls)


# ---------------------------
# 7. Artifact creation contents
# ---------------------------
@pytest.mark.asyncio
async def test_artifact_creation_contents(base_state):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {}

    with patch("requests.get", return_value=mock_response):
        await generate_map(base_state)

    args, kwargs = base_state["process"].create_artifact.await_args

    assert kwargs["mimetype"] == "application/json"
    assert "occurrence" in kwargs["description"]
    assert kwargs["metadata"]["data_source"] == "bold systems"