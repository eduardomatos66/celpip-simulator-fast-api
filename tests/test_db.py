from sqlalchemy import text
from app.core.database import SessionLocal

def test_connection():
    try:
        print("==> Attempting to connect to TiDB Cloud...")
        db = SessionLocal()
        result = db.execute(text("SELECT VERSION()"))
        version = result.scalar()
        print(f"✅ CONNECTION SUCCESSFUL!")
        print(f"✅ TiDB Version: {version}")
        db.close()
    except Exception as e:
        print("❌ CONNECTION FAILED!")
        print(str(e))

if __name__ == "__main__":
    test_connection()
