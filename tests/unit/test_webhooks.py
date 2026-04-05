import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio

@pytest.fixture
def mock_svix():
    with patch("app.api.v1.webhooks.Webhook") as mock:
        yield mock

async def test_clerk_webhook_user_created(client: AsyncClient, mock_svix, db_session):
    # Mock settings secret
    with patch.object(settings, "CLERK_WEBHOOK_SECRET", "test_secret"):
        # Mock svix verification
        mock_instance = mock_svix.return_value
        mock_instance.verify.return_value = {
            "type": "user.created",
            "data": {
                "id": "user_2abc123",
                "email_addresses": [
                    {"id": "email_1", "email_address": "new_user@example.com"}
                ],
                "primary_email_address_id": "email_1",
                "first_name": "New",
                "last_name": "User"
            }
        }

        headers = {
            "svix-id": "msg_1",
            "svix-timestamp": "1234567890",
            "svix-signature": "v1,signature"
        }

        response = await client.post("/api/v1/webhooks/clerk", json={}, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # Verify user was created in DB
        # Refresh the session and query
        db_session.expire_all()
        from app.models.user import User
        user = db_session.query(User).filter(User.clerk_id == "user_2abc123").first()
        assert user is not None, "User should have been created by the webhook"
        assert user.email == "new_user@example.com"
        assert user.full_name == "New User"

async def test_clerk_webhook_invalid_signature(client: AsyncClient, mock_svix):
    with patch.object(settings, "CLERK_WEBHOOK_SECRET", "test_secret"):
        mock_instance = mock_svix.return_value
        from svix.webhooks import WebhookVerificationError
        mock_instance.verify.side_effect = WebhookVerificationError("Invalid")

        headers = {
            "svix-id": "msg_1",
            "svix-timestamp": "1234567890",
            "svix-signature": "v1,invalid"
        }

        response = await client.post("/api/v1/webhooks/clerk", json={}, headers=headers)
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["message"] == "Invalid signature"

async def test_clerk_webhook_missing_secret(client: AsyncClient):
    with patch.object(settings, "CLERK_WEBHOOK_SECRET", ""):
        response = await client.post("/api/v1/webhooks/clerk", json={})
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["message"] == "Webhook configuration error"
