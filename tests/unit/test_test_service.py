import pytest
import json
from unittest.mock import AsyncMock
from app.services import test_service
from app.models.quiz import TestAvailable

@pytest.mark.asyncio
async def test_get_test_available_by_id_cached_disabled(db_session):
    # Pass None for redis_client to simulate REDIS_ENABLED=False
    t = TestAvailable(test_id=99, test_name="TestFallback")
    db_session.add(t)
    db_session.commit()

    result = await test_service.get_test_available_by_id_cached(db_session, None, 99)
    assert str(result["test_id"]) == "99"

@pytest.mark.asyncio
async def test_get_test_available_by_id_cached_hit(db_session):
    mock_redis = AsyncMock()
    cached_data = {"test_id": 100, "test_name": "CachedTest", "test_areas": []}
    mock_redis.get.return_value = json.dumps(cached_data).encode("utf-8")

    result = await test_service.get_test_available_by_id_cached(db_session, mock_redis, 100)
    assert str(result["test_id"]) == "100"
    mock_redis.get.assert_called_once_with("cache:tests:100")
    mock_redis.set.assert_not_called()

@pytest.mark.asyncio
async def test_get_test_available_by_id_cached_miss_and_store(db_session):
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    t = TestAvailable(test_id=101, test_name="TestMiss")
    db_session.add(t)
    db_session.commit()

    result = await test_service.get_test_available_by_id_cached(db_session, mock_redis, 101)

    assert str(result["test_id"]) == "101"
    mock_redis.get.assert_called_once_with("cache:tests:101")
    mock_redis.set.assert_called_once()

@pytest.mark.asyncio
async def test_get_test_available_by_id_cached_miss_not_found(db_session):
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    result = await test_service.get_test_available_by_id_cached(db_session, mock_redis, 404)
    assert result is None
    mock_redis.set.assert_not_called()

@pytest.mark.asyncio
async def test_get_tests_summary_cached_hit(db_session):
    mock_redis = AsyncMock()
    cached_data = [{"test_id": 1, "test_name": "CachedSumm", "test_areas": []}]
    mock_redis.get.return_value = json.dumps(cached_data).encode("utf-8")

    result = await test_service.get_tests_summary_cached(db_session, mock_redis)
    assert len(result) == 1
    assert str(result[0]["test_id"]) == "1"
    mock_redis.get.assert_called_once_with("cache:tests:summary")

@pytest.mark.asyncio
async def test_get_tests_summary_cached_miss(db_session):
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    t = TestAvailable(test_id=105, test_name="TestMissSumm")
    db_session.add(t)
    db_session.commit()

    result = await test_service.get_tests_summary_cached(db_session, mock_redis)
    assert len(result) >= 1
    mock_redis.set.assert_called_once()
