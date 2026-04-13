import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user import UserRole, User, UserStatus
from app.services import user_service, test_result_service
from app.core.deps import get_current_user_claims

# We will override the claims to simulate different users
class MockClaims:
    def __init__(self, clerk_id, email):
        self.clerk_id = clerk_id
        self.email = email

    def get_claims(self):
        return {"sub": self.clerk_id, "email": self.email}

mock_user = MockClaims("test_user_id", "user@example.com")

def override_get_current_user_claims():
    return mock_user.get_claims()

@pytest.mark.asyncio
async def test_role_deletion_permissions(client: AsyncClient, db_session):
    # Override the dependency inside the test to avoid being overwritten by conftest.py
    app.dependency_overrides[get_current_user_claims] = override_get_current_user_claims

    # 1. Setup users with different roles
    admin = user_service.get_or_create_user(db_session, "admin_clerk", "admin@example.com", "Admin User")
    admin.role = UserRole.ADMIN
    admin.status = UserStatus.APPROVED
    db_session.commit()

    best_user = user_service.get_or_create_user(db_session, "best_clerk", "best@example.com", "Best User")
    best_user.role = UserRole.EDITOR
    best_user.status = UserStatus.APPROVED
    db_session.commit()

    regular_user = user_service.get_or_create_user(db_session, "reg_clerk", "reg@example.com", "Reg User")
    regular_user.role = UserRole.USER
    regular_user.status = UserStatus.APPROVED
    db_session.commit()

    # 2. Create a test result for each
    # We need a test first
    from app.models.quiz import TestAvailable
    test = db_session.query(TestAvailable).first()
    if not test:
        test = TestAvailable(test_name="Test 1")
        db_session.add(test)
        db_session.commit()

    from app.models.answer import TestResult
    res_admin = TestResult(user_id=admin.id, available_test_id=test.test_id, clb_average=10)
    res_best = TestResult(user_id=best_user.id, available_test_id=test.test_id, clb_average=10)
    res_reg = TestResult(user_id=regular_user.id, available_test_id=test.test_id, clb_average=10)
    db_session.add_all([res_admin, res_best, res_reg])
    db_session.commit()

    # --- Test 1: Regular User tries to delete own result ---
    mock_user.clerk_id = "reg_clerk"
    mock_user.email = "reg@example.com"

    response = await client.delete(f"/api/v1/test-results/{res_reg.test_result_id}")
    assert response.status_code == 403
    json_data = response.json()
    assert "error" in json_data
    assert "Insufficient permissions" in json_data["error"]["message"]

    # --- Test 2: Editor User deletes own result ---
    mock_user.clerk_id = "best_clerk"
    mock_user.email = "best@example.com"

    response = await client.delete(f"/api/v1/test-results/{res_best.test_result_id}")
    assert response.status_code == 204

    # --- Test 3: Admin deletes own result ---
    mock_user.clerk_id = "admin_clerk"
    mock_user.email = "admin@example.com"

    response = await client.delete(f"/api/v1/test-results/{res_admin.test_result_id}")
    assert response.status_code == 204

    # --- Test 4: Admin tries to delete someone else's result (Regular User's) ---
    # The requirement said "BestUser and Admin can delete THEIR history"
    # and "in the future, admin might be able to handle others history"
    # So currently they should NOT be able to delete others.
    mock_user.clerk_id = "admin_clerk"
    mock_user.email = "admin@example.com"

    response = await client.delete(f"/api/v1/test-results/{res_reg.test_result_id}")
    assert response.status_code == 403
    json_data = response.json()
    assert "error" in json_data
    assert "Not authorized to delete this result" in json_data["error"]["message"]

    # Cleanup overrides
    app.dependency_overrides.clear()
