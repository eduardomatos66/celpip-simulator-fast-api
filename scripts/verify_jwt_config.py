import asyncio
import sys
import os

# Add the project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from app.core.config import settings
from app.core.security import _decode_and_verify
from app.core.logger import logger

async def test_config(token: str = None):
    print("--- JWT Configuration Verifier ---")
    print(f"APP_ENV: {settings.APP_ENV}")
    print(f"CLERK_ISSUER_URL: {settings.CLERK_ISSUER_URL}")
    print(f"CLERK_AUDIENCE: {settings.CLERK_AUDIENCE}")
    print(f"CLERK_JWT_KEY: {'Set (PEM)' if settings.CLERK_JWT_KEY else 'Not set (will use JWKS)'}")

    if not token:
        print("\n[!] No token provided to verify. You can pass a token as an argument:")
        print("    python scripts/verify_jwt_config.py <YOUR_JWT_TOKEN>")
        return

    print(f"\n[ ] Attempting to verify token: {token[:20]}...")
    try:
        claims = await _decode_and_verify(token)
        print("\n[SUCCESS] Token verified successfully!")
        print(f"Subject (Clerk ID): {claims.get('sub')}")
        print(f"Email: {claims.get('email')}")
        print(f"Issuer in Token: {claims.get('iss')}")
        print(f"Audience in Token: {claims.get('aud')}")
    except Exception as e:
        print(f"\n[FAILURE] Verification failed: {e}")
        print("\nTroubleshooting Tips:")
        print("1. If 'Invalid issuer', check if CLERK_ISSUER_URL should have a trailing slash (or vice-versa).")
        print("2. If 'Signature verification failed', ensure CLERK_JWT_KEY is the correct PEM from Clerk.")
        print("3. Check if the token was issued for the correct instance (Dev vs Prod).")

if __name__ == "__main__":
    token_val = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(test_config(token_val))
