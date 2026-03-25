import pytest
from unittest.mock import patch, AsyncMock
from app.core import redis
from app.core.config import settings

@pytest.mark.asyncio
async def test_init_redis_disabled():
    with patch.object(settings, "REDIS_ENABLED", False):
        await redis.init_redis()
        assert redis.redis_client is None

@pytest.mark.asyncio
async def test_init_redis_enabled():
    with patch.object(settings, "REDIS_ENABLED", True):
        with patch("redis.asyncio.from_url", return_value=AsyncMock()) as mock_from_url:
            await redis.init_redis()
            assert redis.redis_client is not None
            mock_from_url.assert_called_once()
            
            # test cleanup
            await redis.close_redis()
            # It should have called close on the mocked instance
            redis.redis_client = None
