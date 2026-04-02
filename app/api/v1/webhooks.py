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

def extract_user_data(data: dict):
    """
    Extract clerk_id, email, and full_name from Clerk user data.
    """
    clerk_id = data.get("id")

    # Extract email from the list of email addresses
    email_addresses = data.get("email_addresses", [])
    primary_email_id = data.get("primary_email_address_id")
    email = ""

    if primary_email_id:
        for email_obj in email_addresses:
            if email_obj.get("id") == primary_email_id:
                email = email_obj.get("email_address", "")
                break

    # Fallback to the first email if primary not found
    if not email and email_addresses:
        email = email_addresses[0].get("email_address", "")

    # Extract names, handling potential nulls
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    # Fallback to external accounts if names are missing at root (common in some OAuth flows)
    if (not first_name or not last_name) and data.get("external_accounts"):
        for ext in data.get("external_accounts", []):
            if not first_name:
                first_name = ext.get("first_name") or ext.get("given_name")
            if not last_name:
                last_name = ext.get("last_name") or ext.get("family_name")
            if first_name and last_name:
                break

    first_name = first_name or ""
    last_name = last_name or ""
    full_name = f"{first_name} {last_name}".strip() or "New User"

    return clerk_id, email, full_name

@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db),
    svix_id: str = Header(None, alias="svix-id"),
    svix_timestamp: str = Header(None, alias="svix-timestamp"),
    svix_signature: str = Header(None, alias="svix-signature"),
):
    """
    Handle Clerk webhooks (user.created, user.updated, etc.)
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

    if event_type in ["user.created", "user.updated"]:
        clerk_id, email, full_name = extract_user_data(data)
        logger.info(f"Processing {event_type} for {clerk_id}: email={email}, full_name={full_name}")

        if clerk_id and email:
            user_service.get_or_create_user(
                db,
                clerk_id=clerk_id,
                email=email,
                full_name=full_name
            )
            logger.info(f"User {clerk_id} synchronized successfully ({event_type})")

    return {"status": "ok"}
