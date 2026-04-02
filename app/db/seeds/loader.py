"""
Legacy SQL loader for CELPIP Simulator.
Parses legacy INSERT statements and maps them to the current SQLAlchemy models.
"""

import re
import os
from typing import List, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import text
import ast

from app.models.quiz import (
    TestAvailable, TestArea, PartIntroduction, Part, Section, Question, Option, AreaTest
)
from app.core.logger import logger

# Regex to find INSERT INTO ... (cols) VALUES (...)
# Handles schema prefixes and backticks.
# Uses a lookahead to find the next INSERT or end of file to avoid stopping at semicolons in strings.
INSERT_RE = re.compile(
    r"INSERT INTO\s+([^\s,\(]+)\s*\((.*?)\)\s*VALUES\s*(.*?)(?=\n\s*INSERT INTO|\Z)",
    re.IGNORECASE | re.DOTALL
)

def parse_sql_values(values_str: str) -> List[List[Any]]:
    """
    Parses the VALUES part of an INSERT statement using a state machine
    to handle strings and nested parentheses correctly.
    """
    values_str = values_str.strip().rstrip(';')
    results = []

    i = 0
    n = len(values_str)

    while i < n:
        # Move to the next '('
        while i < n and values_str[i] != '(':
            i += 1
        if i >= n: break

        # We are at the start of a tuple
        start = i
        i += 1
        in_string = False
        quote_char = None
        bracket_level = 1

        while i < n and bracket_level > 0:
            c = values_str[i]
            if not in_string:
                if c in ("'", '"'):
                    in_string = True
                    quote_char = c
                elif c == '(':
                    bracket_level += 1
                elif c == ')':
                    bracket_level -= 1
            else:
                if c == quote_char:
                    # Check for escaped quote
                    if i > 0 and values_str[i-1] == '\\':
                        pass # Escaped
                    elif i + 1 < n and values_str[i+1] == quote_char:
                        # Some SQL use '' as escaped '
                        i += 1
                    else:
                        in_string = False
            i += 1

        # Tuple captured
        tuple_raw = values_str[start+1:i-1]

        # Now parse the values inside the tuple
        row = []
        # Respect strings when splitting by comma
        v_idx = 0
        v_len = len(tuple_raw)
        while v_idx < v_len:
            # Skip whitespace
            while v_idx < v_len and tuple_raw[v_idx].isspace():
                v_idx += 1
            if v_idx >= v_len: break

            v_start = v_idx
            if tuple_raw[v_idx] in ("'", '"'):
                q = tuple_raw[v_idx]
                v_idx += 1
                while v_idx < v_len:
                    if tuple_raw[v_idx] == q:
                        if v_idx > 0 and tuple_raw[v_idx-1] == '\\':
                            v_idx += 1
                        elif v_idx + 1 < v_len and tuple_raw[v_idx+1] == q:
                            v_idx += 2
                        else:
                            v_idx += 1
                            break
                    else:
                        v_idx += 1
                val_raw = tuple_raw[v_start:v_idx]
                # Cleanup and handle escapes
                item = val_raw[1:-1]
                item = item.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n").replace("\\r", "\r")
                row.append(item)
            else:
                # Find next comma
                while v_idx < v_len and tuple_raw[v_idx] != ',':
                    v_idx += 1
                val_raw = tuple_raw[v_start:v_idx].strip()
                if val_raw.upper() == 'NULL':
                    row.append(None)
                elif val_raw.upper() == 'TRUE':
                    row.append(True)
                elif val_raw.upper() == 'FALSE':
                    row.append(False)
                else:
                    try:
                        if '.' in val_raw:
                            row.append(float(val_raw))
                        else:
                            row.append(int(val_raw))
                    except ValueError:
                        row.append(val_raw)

            # Skip the comma
            while v_idx < v_len and tuple_raw[v_idx] != ',':
                v_idx += 1
            v_idx += 1

        results.append(row)
    return results

def get_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    results = []
    for match in INSERT_RE.finditer(content):
        # Extract columns and clean them up
        raw_cols = match.group(2)
        columns = [c.strip().strip('`').strip('"') for c in raw_cols.split(',')]

        values_str = match.group(3)
        values_list = parse_sql_values(values_str)

        for values in values_list:
            if len(columns) == len(values):
                results.append(dict(zip(columns, values)))
            else:
                 logger.error(f"Column/Value mismatch in {file_path}: {len(columns)} cols vs {len(values)} vals")
    return results

class LegacyDataLoader:
    def __init__(self, db: Session, legacy_dir: str):
        self.db = db
        self.legacy_dir = legacy_dir
        self.junctions = {} # Stores junction table data: table_name -> map

    def load_all(self):
        """Main entry point for loading data in order."""
        logger.info("Starting legacy data migration...")

        # 1. Test Available
        self._load_test_available()

        # 2. Part Introductions
        self._load_part_introductions()

        # 3. Parts
        self._load_parts()

        # 4. Junctions needed for relationships
        self._load_junctions()

        # 5. Test Areas (links to TestAvailable and Part)
        self._load_test_areas()

        # 6. Sections (links to Part)
        self._load_sections()

        # 7. Questions (links to Section)
        self._load_questions()

        # 8. Options (links to Question)
        self._load_options()

        logger.info("Legacy data migration completed.")

    def _load_test_available(self):
        data = get_data_from_file(os.path.join(self.legacy_dir, "00_create_exams.sql"))
        for item in data:
            test_id = item.get('available_test_id') or item.get('id')
            test_name = item.get('test_name') or item.get('exam_name')

            obj = TestAvailable(
                test_id=test_id,
                test_name=test_name
            )
            self.db.merge(obj)
        self.db.commit()

    def _load_part_introductions(self):
        data = get_data_from_file(os.path.join(self.legacy_dir, "06_create_part_introductions.sql"))
        for item in data:
            obj = PartIntroduction(
                part_introduction_id=item.get('part_introduction_id') or item.get('id'),
                text=item.get('text'),
                auxiliary_texts=item.get('auxiliary_texts') or item.get('aux_text')
            )
            self.db.merge(obj)
        self.db.commit()

    def _load_parts(self):
        data = get_data_from_file(os.path.join(self.legacy_dir, "04_create_parts.sql"))
        for item in data:
            obj = Part(
                part_id=item.get('part_id') or item.get('id'),
                part_name=item.get('part_name') or item.get('name'),
                text_question_content=item.get('text_question_content'),
                time=item.get('time'),
                part_number=item.get('part_number'),
                questions_type=item.get('questions_type'),
                introduction_id=item.get('introduction_part_introduction_id') or item.get('introduction_id')
            )
            self.db.merge(obj)
        self.db.commit()

    def _load_junctions(self):
        self.junctions['exam_areas'] = get_data_from_file(os.path.join(self.legacy_dir, "03_create_test_available_test_areas.sql"))
        self.junctions['area_parts'] = get_data_from_file(os.path.join(self.legacy_dir, "05_create_test_areas_parts.sql"))
        self.junctions['part_sections'] = get_data_from_file(os.path.join(self.legacy_dir, "08_create_parts_sections.sql"))
        self.junctions['section_questions'] = get_data_from_file(os.path.join(self.legacy_dir, "10_create_sections_questions.sql"))
        self.junctions['question_options'] = get_data_from_file(os.path.join(self.legacy_dir, "12_create_questions_options.sql"))

    def _load_test_areas(self):
        data = get_data_from_file(os.path.join(self.legacy_dir, "02_create_test_areas.sql"))

        # Mapping helpers with correct legacy keys
        area_to_exam = {j.get('test_areas_area_id'): j.get('test_available_available_test_id')
                       for j in self.junctions['exam_areas']}
        area_to_part = {j.get('test_area_area_id'): j.get('parts_part_id')
                       for j in self.junctions['area_parts']}

        for item in data:
            area_id = item.get('area_id') or item.get('id')
            area_name = item.get('area_name') or item.get('type') or ""
            obj = TestArea(
                test_area_id=area_id,
                area=AreaTest(area_name.lower()),
                available_test_id=area_to_exam.get(area_id),
                part_id=area_to_part.get(area_id)
            )
            self.db.merge(obj)
        self.db.commit()

    def _load_sections(self):
        data = get_data_from_file(os.path.join(self.legacy_dir, "07_create_sections.sql"))
        section_to_part = {j.get('sections_id') or j.get('section_id'): j.get('part_part_id') or j.get('part_id')
                          for j in self.junctions['part_sections']}

        for item in data:
            sec_id = item.get('section_id') or item.get('id')
            obj = Section(
                section_id=sec_id,
                text=item.get('text'),
                time=item.get('time'),
                section_audio_link=item.get('section_audio_link') or item.get('audio_link'),
                section_image_link=item.get('section_image_link') or item.get('image_link'),
                section_video_link=item.get('section_video_link') or item.get('video_link'),
                text_question_content=item.get('text_question_content'),
                section_number=item.get('section_number'),
                part_id=section_to_part.get(sec_id)
            )
            self.db.merge(obj)
        self.db.commit()

    def _load_questions(self):
        data = get_data_from_file(os.path.join(self.legacy_dir, "09_create_questions.sql"))
        q_to_sec = {j.get('questions_id') or j.get('question_id'): j.get('section_id')
                   for j in self.junctions['section_questions']}

        for item in data:
            q_id = item.get('question_id') or item.get('id')
            obj = Question(
                question_id=q_id,
                text=item.get('text'),
                time=item.get('time'),
                audio_link=item.get('audio_link'),
                question_number=item.get('question_number'),
                section_id=q_to_sec.get(q_id)
            )
            self.db.merge(obj)
        self.db.commit()

    def _load_options(self):
        data = get_data_from_file(os.path.join(self.legacy_dir, "11_create_options.sql"))
        opt_to_q = {j.get('options_id') or j.get('option_id'): j.get('question_id')
                   for j in self.junctions['question_options']}

        for item in data:
            opt_id = item.get('option_id') or item.get('id')
            obj = Option(
                option_id=opt_id,
                text=item.get('text'),
                is_correct=bool(item.get('is_correct')),
                question_id=opt_to_q.get(opt_id)
            )
            self.db.merge(obj)
        self.db.commit()
