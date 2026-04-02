import pytest
from unittest.mock import patch, MagicMock
from app.services.internal.ollama3_api_service import get_ollama3_response, parse_ollama3_response

@pytest.mark.asyncio
async def test_get_ollama3_response_success():
    # Mock httpx.AsyncClient.post
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"response": '{"generalAverageCLB": {"gradeCLB": 9}}'}
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        evaluation = await get_ollama3_response("Test prompt")
        assert evaluation is not None
        assert evaluation.generalAverageCLB.gradeCLB == 9

@pytest.mark.asyncio
async def test_get_ollama3_response_network_error():
    with patch("httpx.AsyncClient.post", side_effect=Exception("Network down")):
        evaluation = await get_ollama3_response("Test prompt")
        assert evaluation is None

def test_parse_ollama3_response_valid_json():
    # Test valid JSON
    response_text = 'Here is the score: {"generalAverageCLB": {"gradeCLB": 10}}'
    evaluation = parse_ollama3_response(response_text)
    assert evaluation is not None
    assert evaluation.generalAverageCLB.gradeCLB == 10

def test_parse_ollama3_response_missing_bracket_fix():
    # Test JSON missing closing bracket (mimics Java fallback behavior)
    response_text = '{"generalAverageCLB": {"gradeCLB": 7}'
    evaluation = parse_ollama3_response(response_text)
    assert evaluation is not None
    assert evaluation.generalAverageCLB.gradeCLB == 7

def test_parse_ollama3_response_invalid_json():
    # Test completely invalid JSON that can't be fixed by appending "}"
    response_text = '{ bad json format '
    evaluation = parse_ollama3_response(response_text)
    assert evaluation is None

def test_parse_ollama3_response_no_json():
    response_text = "There is no JSON block here."
    evaluation = parse_ollama3_response(response_text)
    assert evaluation is None
