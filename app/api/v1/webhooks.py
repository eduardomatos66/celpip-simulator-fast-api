from fastapi import APIRouter, Header, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError
import json

from app.core.config import settings
from app.core.deps import get_db
from app.core.logger import logger
from app.services import user_service
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db),
    svix_id: str = Header(None, alias="svix-id"),
    svix_timestamp: str = Header(None, alias="svix-timestamp"),
    svix_signature: str = Header(None, alias="svix-signature"),
):
    """
    Handle Clerk webhooks (user.created, etc.)
    """
    if not settings.CLERK_WEBHOOK_SECRET:
        logger.error("CLERK_WEBHOOK_SECRET is not set. Cannot verify webhook.")
        raise HTTPException(status_code=500, detail="Webhook configuration error")

    payload = await request.body()
    headers = {
        "svix-id": svix_id,
        "svix-timestamp": svix_timestamp,
        "svix-signature": svix_signature,
    }

    wh = Webhook(settings.CLERK_WEBHOOK_SECRET)

    try:
        msg = wh.verify(payload, headers)
    except WebhookVerificationError as e:
        logger.warning(f"Invalid webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = msg.get("type")
    data = msg.get("data")

    logger.info(f"Received Clerk webhook: {event_type}")

    if event_type == "user.created":
        clerk_id = data.get("id")
        email = data.get("email_addresses", [{}])[0].get("email_address")
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or "New User"

        if clerk_id and email:
            logger.info(f"Provisioning new user from webhook: {email}")
            user_service.get_or_create_user(
                db, 
                clerk_id=clerk_id, 
                email=email, 
                full_name=full_name
            )
            # Future: trigger "Under Review" email here

    return {"status": "ok"}
