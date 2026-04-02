import pytest
from app.core.database import get_db, Base
from unittest.mock import patch, MagicMock

def test_get_db_generator():
    db_gen = get_db()
    with patch("app.core.database.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Next yields the db
        db_instance = next(db_gen)
        assert db_instance == mock_db

        # Completing the generator closes the db
        with pytest.raises(StopIteration):
            next(db_gen)
        mock_db.close.assert_called_once()
