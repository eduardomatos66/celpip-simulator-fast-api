import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.seeds.loader import LegacyDataLoader
from app.core.database import SessionLocal
from app.core.logger import logger

def main():
    # Migration from legacy sql files to new database
    legacy_dir = r"E:\Workspace\celpip-simulator\celpip-server\src\main\resources\sql_files"

    # Check if legacy dir exists
    if not os.path.exists(legacy_dir):
        logger.error(f"Legacy directory not found: {legacy_dir}")
        sys.exit(1)

    db = SessionLocal()
    try:
        loader = LegacyDataLoader(db, legacy_dir)
        loader.load_all()
        logger.info("Database seeding finished successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during seeding: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
