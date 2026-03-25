import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

def test_lifespan_integration():
    with patch("app.main.init_redis") as mock_init:
        with patch("app.main.close_redis") as mock_close:
            with TestClient(app) as client:
                mock_init.assert_called_once()
            mock_close.assert_called_once()
