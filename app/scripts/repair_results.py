import sys
import os
from sqlalchemy.orm import Session

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import SessionLocal
from app.models.answer import TestResult
from app.services.test_result_service import calculate_exam_score

def repair_results():
    db = SessionLocal()
    try:
        # Find results that are likely broken (lumped into reading)
        # Criteria: listening_max is 0 and reading_max is suspiciously high (e.g. > 50)
        # or listening_max is 0 but we have an answer sheet associated.
        results_to_fix = db.query(TestResult).filter(
            TestResult.listening_max == 0,
            TestResult.reading_max > 0,
            TestResult.answer_sheet_id != None
        ).all()

        print(f"Found {len(results_to_fix)} potentially broken results.")

        for res in results_to_fix:
            print(f"Repairing result {res.test_result_id} (AnswerSheet {res.answer_sheet_id})...")

            # Delete the old result record to avoid duplicates if calculate_exam_score adds a new one
            # Actually, calculate_exam_score adds a new one to the DB.
            # We should probably pass a flag or just delete the old one first.

            sheet_id = res.answer_sheet_id
            test_id = str(res.available_test_id)
            user_id = res.user_id

            db.delete(res)
            db.commit() # Commit delete first

            new_res = calculate_exam_score(db, sheet_id, test_id, user_id)
            if new_res:
                print(f"  -> Fixed! New Listening Max: {new_res.listening_max}, Reading Max: {new_res.reading_max}")
            else:
                print(f"  -> Failed to recalculate for {res.test_result_id}")

        print("Repair complete.")
    finally:
        db.close()

if __name__ == "__main__":
    repair_results()
