import pytest
from app.services import test_area_service
from app.schemas.quiz import TestAreaCreate, TestAreaUpdate
from app.models.quiz import AreaTest, TestArea

def test_create_get_delete_test_area(db_session):
    # Create
    ta_in = TestAreaCreate(area=AreaTest.READING, part_id=None)
    created_ta = test_area_service.create_test_area(db_session, ta_in)
    assert created_ta.test_area_id is not None
    assert created_ta.area == AreaTest.READING

    # Get All
    test_areas = test_area_service.get_test_areas(db_session)
    assert len(test_areas) >= 1
    assert any(t.test_area_id == created_ta.test_area_id for t in test_areas)

    # Get By ID
    fetched_ta = test_area_service.get_test_area_by_id(db_session, created_ta.test_area_id)
    assert fetched_ta is not None
    assert fetched_ta.test_area_id == created_ta.test_area_id

    # Update
    ta_update = TestAreaUpdate(area=AreaTest.WRITING, part_id=None)
    updated_ta = test_area_service.update_test_area(db_session, fetched_ta, ta_update)
    assert updated_ta.area == AreaTest.WRITING

    # Delete
    deleted = test_area_service.delete_test_area(db_session, created_ta.test_area_id)
    assert deleted is True

    # Confirm deletion
    missing_ta = test_area_service.get_test_area_by_id(db_session, created_ta.test_area_id)
    assert missing_ta is None

def test_delete_missing_test_area(db_session):
    deleted = test_area_service.delete_test_area(db_session, 99999)
    assert deleted is False
