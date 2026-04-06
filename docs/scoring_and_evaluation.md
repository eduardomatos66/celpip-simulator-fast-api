# 9. Scoring and Evaluation Logic

This document describes how the CELPIP Simulator API evaluates user answers and calculates scores for Listening and Reading components.

## Overview

The CELPIP test contains multiple-choice questions (MCQs) for Listening and Reading. These are automatically scored by the backend upon submission of an **Answer Sheet**.

---

## 1. Answer Sheet Submission

When a user submits an answer sheet via `POST /api/v1/answer-sheets/submit`, the `AnswerSheetService` performs the following steps for each question:

### ID vs. Text Resolution
To ensure compatibility with various frontend implementations:
- If `user_answer` is a numeric string (e.g., `"123"`), the system treats it as an **Option ID**.
- If `question_id` is an alphanumeric string following the pattern `t{T}-area-p{P}-s{S}-q{Q}` (e.g., `"t1-listening-p1-s1-q1"`), the system **automatically resolves** it to the numeric Database Primary Key by performing a hierarchical lookup.
- Both the `user_answer` and the `correct_answer` are stored as **Text** in the `OptionAnswer` table.

> [!TIP]
> This dual-resolution ensures that scoring works even if the frontend only knows the ID of the selected choice.

---

## 2. Automated Scoring Mechanism

Scoring is triggered immediately after submission via the `calculate_exam_score` function in `TestResultService`.

### HTML-Aware Comparison
CELPIP data often contains HTML tags for formatting (e.g., `<p>`, `<span>`). To ensure accurate grading:
- The system uses a dedicated `_clean_text` helper.
- **HTML Stripping**: All tags are removed using regex.
- **Normalization**: Multiple whitespaces are collapsed, and the string is converted to lowercase.
- **Comparison**: The "cleaned" user answer is compared against the "cleaned" correct answer.

### Dynamic Area Mapping
Unlike earlier versions that used a 50/50 split, the system now dynamically identifies the test area for every question:
1. It traces the hierarchy: `Question` → `Section` → `Part` → `TestArea`.
2. It increments the `correct` and `total` counts for the specific area (Listening or Reading).
3. This allows for accurate sub-scores even if the number of questions in each area is unbalanced.

---

## 3. Score Calculation (CLB Mapping)

The CLB (Canadian Language Benchmark) levels are calculated based on the percentage of correct answers:

| Percentage Range | CLB Level |
|------------------|-----------|
| ≥ 90% | 10 |
| ≥ 80% | 9 |
| ≥ 70% | 8 |
| ≥ 60% | 7 |
| ≥ 50% | 6 |
| < 50% | 3-5 |

> [!NOTE]
> Writing and Speaking components currently return placeholder scores (0.0) as they typically require manual grading or AI-based evaluation in separate workflows.
