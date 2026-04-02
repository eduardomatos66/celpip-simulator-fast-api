import sys
import os
from sqlalchemy import text
from app.core.database import SessionLocal

def verify():
    db = SessionLocal()
    tables = [
        "test_available",
        "test_area",
        "part_introduction",
        "part",
        "section",
        "question",
        "question_option"
    ]
    print(f"{'Table':<20} | {'Count':<10}")
    print("-" * 35)
    for table in tables:
        count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"{table:<20} | {count:<10}")
    db.close()

if __name__ == "__main__":
    verify()
