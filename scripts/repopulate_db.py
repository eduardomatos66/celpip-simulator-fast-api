import os
import sys
import re
from sqlalchemy import text

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.core.database import engine, Base
from app.core.config import settings
from app.models.quiz import (
    TestAvailable, TestArea, Part, Section, Question, Option,
    PartIntroduction, test_available_test_areas, test_area_parts,
    part_sections, section_questions, question_options
)

SQL_FILES_DIR = r"E:\Workspace\celpip-simulator\celpip-server\src\main\resources\sql_files"
SQL_FILES = [
    "00_create_exams.sql",
    "02_create_test_areas.sql",
    "03_create_test_available_test_areas.sql",
    "04_create_parts.sql",
    "05_create_test_areas_parts.sql",
    "06_create_part_introductions.sql",
    "07_create_sections.sql",
    "08_create_parts_sections.sql",
    "09_create_questions.sql",
    "10_create_sections_questions.sql",
    "11_create_options.sql",
    "12_create_questions_options.sql",
]

def clean_sql(sql: str) -> str:
    """Remove database prefix and handle potential syntax issues."""
    sql = sql.replace("`celpip-simulator`.", "")
    sql = re.sub(r"(?i)^USE\s+.*;", "", sql, flags=re.MULTILINE)
    return sql

def main():
    print(f"Connecting to database: {settings.TIDB_DATABASE}")
    engine.echo = False

    tables_to_drop = [
        "question_options", "questions_options",
        "section_questions", "sections_questions",
        "part_sections", "parts_sections",
        "test_area_parts", "test_areas_parts",
        "test_available_test_areas",
        "question_option",
        "question",
        "section",
        "part",
        "part_introduction",
        "test_area",
        "test_available"
    ]

    with engine.connect() as conn:
        print("Cleaning up tables for scorched earth recreation...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for table in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
                print(f"Dropped {table}")
            except Exception as e:
                print(f"Could not drop {table}: {e}")
        conn.commit()

    # 2. Recreate all tables via SQLAlchemy
    print("Ensuring tables and junction tables exist (recreating from models)...")
    Base.metadata.create_all(engine)

    with engine.connect() as conn:
        # 3. Execute SQL files
        print("\nStarting data population...")
        for sql_file in SQL_FILES:
            file_path = os.path.join(SQL_FILES_DIR, sql_file)
            if not os.path.exists(file_path):
                print(f"WARNING: File {sql_file} not found")
                continue

            print(f"Executing {sql_file}...")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            print(f"Executing {sql_file}...")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            cleaned_content = clean_sql(content)

            # Robust split: Split on semicolon followed by newline or end of file
            # This handles both files with many separate INSERT statements (one per line)
            # and files with one giant INSERT statement.
            statements = [s.strip() for s in re.split(r';\s*(?:\n|$)', cleaned_content) if s.strip()]
            print(f"Found {len(statements)} statements in {sql_file}")

            for i, stmt in enumerate(statements):
                try:
                    # Append semicolon back if it was stripped and it's needed (though text() usually doesnt care)
                    conn.execute(text(stmt))
                    if len(statements) > 100 and i % 100 == 0:
                        sys.stdout.write(f"  Executed {i}/{len(statements)} statements...\r")
                        sys.stdout.flush()
                except Exception as e:
                    # Only log errors, don't stop the whole file
                    msg = str(e).encode('ascii', 'ignore').decode('ascii')
                    print(f"\nError in {sql_file} at stmt {i}: {msg}")
                    safe_stmt = stmt[:100].encode('ascii', 'ignore').decode('ascii')
                    print(f"Stmt preview: {safe_stmt}...")

            conn.commit()
            print(f"\nCompleted {sql_file}")

        # Final Row Check
        print("\n--- FINAL ROW COUNTS ---")
        final_tables = [
            "test_available", "test_area", "test_available_test_areas",
            "part", "test_area_parts", "section", "part_sections",
            "question", "section_questions", "question_option", "question_options"
        ]
        for table in final_tables:
            try:
                res = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                print(f"{table}: {res.scalar()} rows")
            except Exception as e:
                print(f"{table}: ERROR {e}")

    print("\nData population complete!")

if __name__ == "__main__":
    main()
