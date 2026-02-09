"""
Unit tests for CRUD operations in Estudei Offline.
Run with: pytest tests/test_crud.py -v
"""

import pytest
import sqlite3
import os
import sys
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.database import DatabaseManager


def build_test_db(tmp_path):
    test_db = DatabaseManager.__new__(DatabaseManager)
    test_db.DB_NAME = str(tmp_path / "test_estudei.db")
    test_db._local = threading.local()
    test_db._init_lock = threading.Lock()
    test_db._initialized = False
    test_db._connections = []
    test_db._connections_lock = threading.Lock()
    test_db.init_db()
    return test_db


class TestDatabaseManager:
    """Tests for the DatabaseManager class."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup a fresh test database for each test."""
        self.db = build_test_db(tmp_path)
        
        yield
        
        # Cleanup
        self.db.close_all()
    
    def test_connection_created(self):
        """Test that database connection is properly created."""
        conn = self.db.get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
    
    def test_tables_created(self):
        """Test that all required tables are created."""
        cursor = self.db.get_connection().cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            'subjects', 'study_sessions', 'mock_exams', 'mock_exam_items',
            'topics', 'reminders', 'plans', 'plan_subjects'
        }
        
        for table in expected_tables:
            assert table in tables, f"Table '{table}' not found"
    
    def test_seed_data_inserted(self):
        """Test that seed data is inserted on first run."""
        result = self.db.fetch_all("SELECT * FROM subjects")
        assert len(result) > 0, "Seed data not inserted"
    
    def test_execute_query_insert(self):
        """Test inserting data via execute_query."""
        cursor = self.db.execute_query(
            "INSERT INTO subjects (name, category) VALUES (?, ?)",
            ("Test Subject", "Test Category")
        )
        assert cursor.lastrowid is not None
    
    def test_fetch_one(self):
        """Test fetching a single row."""
        result = self.db.fetch_one("SELECT * FROM subjects LIMIT 1")
        assert result is not None
        assert 'name' in result.keys()


class TestSubjectsCRUD:
    """Tests for Subjects CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test database and import crud module."""
        # Patch the database before importing crud
        import src.data.database as database_module
        original_db = database_module.db
        
        # Create test database
        test_db = build_test_db(tmp_path)
        
        # Replace global db instance
        database_module.db = test_db
        self.db = test_db
        
        # Import crud after patching
        import importlib
        import src.data.crud as crud_module
        importlib.reload(crud_module)
        self.crud = crud_module
        
        yield
        
        # Restore original
        database_module.db = original_db
        test_db.close_all()
    
    def test_get_all_subjects(self):
        """Test retrieving all subjects."""
        subjects = self.crud.get_all_subjects()
        assert len(subjects) > 0
        assert 'name' in subjects[0].keys()
    
    def test_add_subject_return_id(self):
        """Test adding a new subject and getting its ID."""
        new_id = self.crud.add_subject_return_id("Nova Matéria", "Categoria", "#ff0000")
        assert new_id is not None
        assert isinstance(new_id, int)
        
        # Verify it was inserted
        subject = self.crud.get_subject_by_id(new_id)
        assert subject is not None
        assert subject['name'] == "Nova Matéria"
        assert subject['color'] == "#ff0000"
    
    def test_get_subject_by_id(self):
        """Test retrieving a subject by ID."""
        subjects = self.crud.get_all_subjects()
        first_id = subjects[0]['id']
        
        subject = self.crud.get_subject_by_id(first_id)
        assert subject is not None
        assert subject['id'] == first_id
    
    def test_update_subject_details(self):
        """Test updating subject details."""
        new_id = self.crud.add_subject_return_id("Original", "Cat", "#000000")
        
        self.crud.update_subject_details(new_id, "Updated Name", "#ffffff")
        
        subject = self.crud.get_subject_by_id(new_id)
        assert subject['name'] == "Updated Name"
        assert subject['color'] == "#ffffff"

    def test_delete_subject_cascades(self):
        """Test deleting a subject removes related data."""
        subject_id = self.crud.add_subject_return_id("To Delete", "Cat", "#123456")
        self.crud.add_topic(subject_id, "Topic 1")
        self.crud.add_study_session(subject_id, "Sessão", 1200, "TEORIA")

        plan_id = self.crud.add_plan("Plan", "Obs", subject_ids=[subject_id])
        cursor = self.db.execute_query(
            "INSERT INTO mock_exams (name, date, score, total_questions) VALUES (?, ?, ?, ?)",
            ("Mock", "2024-01-01", 80.0, 10),
        )
        exam_id = cursor.lastrowid
        self.crud.add_mock_exam_items_bulk(exam_id, [(subject_id, 1.0, 5, 2, 0)])

        self.crud.delete_subject(subject_id)

        assert self.crud.get_subject_by_id(subject_id) is None
        assert self.db.fetch_all("SELECT * FROM topics WHERE subject_id = ?", (subject_id,)) == []
        assert self.db.fetch_all("SELECT * FROM study_sessions WHERE subject_id = ?", (subject_id,)) == []
        assert self.db.fetch_all("SELECT * FROM plan_subjects WHERE plan_id = ?", (plan_id,)) == []
        assert self.db.fetch_all("SELECT * FROM mock_exam_items WHERE subject_id = ?", (subject_id,)) == []


class TestStudySessionsCRUD:
    """Tests for Study Sessions CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test database."""
        import src.data.database as database_module
        original_db = database_module.db
        
        test_db = build_test_db(tmp_path)
        
        database_module.db = test_db
        self.db = test_db
        
        import importlib
        import src.data.crud as crud_module
        importlib.reload(crud_module)
        self.crud = crud_module
        
        yield
        
        database_module.db = original_db
        test_db.close_all()
    
    def test_add_study_session(self):
        """Test adding a study session."""
        subjects = self.crud.get_all_subjects()
        subject_id = subjects[0]['id']
        
        # Add a session
        self.crud.add_study_session(
            subject_id=subject_id,
            topic="Test Topic",
            duration_seconds=3600,
            type_label="TEORIA",
            correct=10,
            wrong=2
        )
        
        # Verify it was added
        sessions = self.crud.get_recent_sessions(1)
        assert len(sessions) == 1
        assert sessions[0]['topic'] == "Test Topic"
        assert sessions[0]['duration_seconds'] == 3600
    
    def test_get_recent_sessions(self):
        """Test retrieving recent sessions."""
        subjects = self.crud.get_all_subjects()
        subject_id = subjects[0]['id']
        
        # Add multiple sessions
        for i in range(5):
            self.crud.add_study_session(subject_id, f"Topic {i}", 1800, "QUESTOES")
        
        sessions = self.crud.get_recent_sessions(3)
        assert len(sessions) == 3
    
    def test_get_total_study_time(self):
        """Test calculating total study time."""
        subjects = self.crud.get_all_subjects()
        subject_id = subjects[0]['id']
        
        self.crud.add_study_session(subject_id, "T1", 3600, "TEORIA")
        self.crud.add_study_session(subject_id, "T2", 1800, "TEORIA")
        
        total = self.crud.get_total_study_time()
        assert total == 5400  # 3600 + 1800

    def test_normalize_study_session_types(self):
        """Test normalization of legacy study session type labels."""
        subjects = self.crud.get_all_subjects()
        subject_id = subjects[0]['id']
        self.db.execute_query(
            "INSERT INTO study_sessions (subject_id, topic, date, duration_seconds, type) VALUES (?, ?, ?, ?, ?)",
            (subject_id, "Legacy", "2024-01-01 10:00:00", 600, "QUESTOES"),
        )
        cursor = self.db.get_connection().cursor()
        self.db._run_migrations(cursor)
        self.db.get_connection().commit()

        result = self.db.fetch_one(
            "SELECT type FROM study_sessions WHERE topic = ?",
            ("Legacy",),
        )
        assert result["type"] == "QUESTÕES"
    
    def test_delete_study_session(self):
        """Test deleting a study session."""
        subjects = self.crud.get_all_subjects()
        subject_id = subjects[0]['id']
        
        self.crud.add_study_session(subject_id, "To Delete", 1000, "TEORIA")
        
        sessions = self.crud.get_recent_sessions(1)
        session_id = sessions[0]['id']
        
        self.crud.delete_study_session(session_id)
        
        # Verify deleted
        remaining = self.crud.get_recent_sessions(10)
        for s in remaining:
            assert s['id'] != session_id


class TestMockExamsCRUD:
    """Tests for Mock Exams CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test database."""
        import src.data.database as database_module
        original_db = database_module.db
        
        test_db = build_test_db(tmp_path)
        
        database_module.db = test_db
        self.db = test_db
        
        import importlib
        import src.data.crud as crud_module
        importlib.reload(crud_module)
        self.crud = crud_module
        
        yield
        
        database_module.db = original_db
        test_db.close_all()
    
    def test_add_mock_exam(self):
        """Test adding a mock exam."""
        self.crud.add_mock_exam("Simulado TRT", "2024-01-15", 85.5, 100, "02:30")
        
        exams = self.crud.get_mock_exams()
        assert len(exams) == 1
        assert exams[0]['name'] == "Simulado TRT"
        assert exams[0]['score'] == 85.5
    
    def test_add_mock_exam_items_bulk(self):
        """Test bulk inserting mock exam items."""
        # First add an exam
        cursor = self.db.execute_query(
            "INSERT INTO mock_exams (name, date, score, total_questions) VALUES (?, ?, ?, ?)",
            ("Test Exam", "2024-01-01", 80.0, 50)
        )
        exam_id = cursor.lastrowid
        
        subjects = self.crud.get_all_subjects()
        
        # Add items for first 3 subjects
        items_data = [
            (subjects[0]['id'], 1.0, 10, 2, 0),
            (subjects[1]['id'], 1.5, 8, 4, 1),
            (subjects[2]['id'], 2.0, 12, 3, 0),
        ]
        
        self.crud.add_mock_exam_items_bulk(exam_id, items_data)
        
        # Verify items were added
        items = self.crud.get_mock_exam_items(exam_id)
        assert len(items) == 3
    
    def test_delete_mock_exam(self):
        """Test deleting a mock exam and its items."""
        # Add exam
        cursor = self.db.execute_query(
            "INSERT INTO mock_exams (name, date, score, total_questions) VALUES (?, ?, ?, ?)",
            ("To Delete", "2024-01-01", 70.0, 30)
        )
        exam_id = cursor.lastrowid
        
        # Add some items
        subjects = self.crud.get_all_subjects()
        self.crud.add_mock_exam_items_bulk(exam_id, [(subjects[0]['id'], 1.0, 5, 5, 0)])
        
        # Delete
        self.crud.delete_mock_exam(exam_id)
        
        # Verify exam deleted
        exams = self.crud.get_mock_exams()
        for e in exams:
            assert e['id'] != exam_id
        
        # Verify items deleted
        items = self.crud.get_mock_exam_items(exam_id)
        assert len(items) == 0


class TestPlansCRUD:
    """Tests for Plans CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test database."""
        import src.data.database as database_module
        original_db = database_module.db
        
        test_db = build_test_db(tmp_path)
        
        database_module.db = test_db
        self.db = test_db
        
        import importlib
        import src.data.crud as crud_module
        importlib.reload(crud_module)
        self.crud = crud_module
        
        yield
        
        database_module.db = original_db
        test_db.close_all()
    
    def test_add_plan_without_subjects(self):
        """Test adding a plan without subjects."""
        plan_id = self.crud.add_plan("Concurso INSS", "Edital 2024")
        
        assert plan_id is not None
        
        plan = self.crud.get_plan_by_id(plan_id)
        assert plan['name'] == "Concurso INSS"
        assert plan['observations'] == "Edital 2024"
    
    def test_add_plan_with_subjects(self):
        """Test adding a plan with associated subjects."""
        subjects = self.crud.get_all_subjects()
        subject_ids = [subjects[0]['id'], subjects[1]['id']]
        
        plan_id = self.crud.add_plan("Plano Completo", "Com disciplinas", subject_ids=subject_ids)
        
        # Verify subjects are linked
        linked_subjects = self.crud.get_subjects_by_plan(plan_id)
        assert len(linked_subjects) == 2
    
    def test_add_subject_to_plan(self):
        """Test linking a subject to an existing plan."""
        plan_id = self.crud.add_plan("Plano Vazio", "")
        subjects = self.crud.get_all_subjects()
        
        self.crud.add_subject_to_plan(plan_id, subjects[0]['id'])
        
        linked = self.crud.get_subjects_by_plan(plan_id)
        assert len(linked) == 1
    
    def test_add_subject_to_plan_duplicate(self):
        """Test that adding duplicate subject doesn't raise error."""
        plan_id = self.crud.add_plan("Test", "")
        subjects = self.crud.get_all_subjects()
        
        # Add same subject twice - should not raise
        self.crud.add_subject_to_plan(plan_id, subjects[0]['id'])
        self.crud.add_subject_to_plan(plan_id, subjects[0]['id'])
        
        linked = self.crud.get_subjects_by_plan(plan_id)
        assert len(linked) == 1  # Still only one
    
    def test_remove_subject_from_plan(self):
        """Test removing a subject from a plan."""
        subjects = self.crud.get_all_subjects()
        plan_id = self.crud.add_plan("To Remove", "", subject_ids=[subjects[0]['id']])
        
        self.crud.remove_subject_from_plan(plan_id, subjects[0]['id'])
        
        linked = self.crud.get_subjects_by_plan(plan_id)
        assert len(linked) == 0
    
    def test_archive_plan(self):
        """Test archiving a plan."""
        plan_id = self.crud.add_plan("To Archive", "")
        
        self.crud.archive_plan(plan_id)
        
        # Should not appear in non-archived list
        active_plans = self.crud.get_plans(archived=0)
        for p in active_plans:
            assert p['id'] != plan_id
        
        # Should appear in archived list
        archived_plans = self.crud.get_plans(archived=1)
        found = any(p['id'] == plan_id for p in archived_plans)
        assert found


class TestRemindersCRUD:
    """Tests for Reminders CRUD operations."""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test database."""
        import src.data.database as database_module
        original_db = database_module.db
        
        test_db = build_test_db(tmp_path)
        
        database_module.db = test_db
        self.db = test_db
        
        import importlib
        import src.data.crud as crud_module
        importlib.reload(crud_module)
        self.crud = crud_module
        
        yield
        
        database_module.db = original_db
        test_db.close_all()
    
    def test_add_reminder(self):
        """Test adding a reminder."""
        self.crud.add_reminder("Estudar para prova", "Estudo", "2024-01-20 10:00")
        
        reminders = self.crud.get_reminders()
        assert len(reminders) >= 1
    
    def test_get_reminders_only_pending(self):
        """Test that get_reminders only returns pending (status=0)."""
        self.crud.add_reminder("Pending", "Cat", "2024-01-01 10:00")
        
        reminders = self.crud.get_reminders()
        pending_id = reminders[0]['id']
        
        # Mark as done
        self.crud.update_reminder_status(pending_id, 1)
        
        # Should not appear anymore
        updated_reminders = self.crud.get_reminders()
        for r in updated_reminders:
            assert r['id'] != pending_id
    
    def test_update_reminder_status(self):
        """Test updating reminder status."""
        self.crud.add_reminder("Test", "Cat", "2024-01-01")
        
        reminders = self.crud.get_reminders()
        rid = reminders[0]['id']
        
        # Set to Done (1)
        self.crud.update_reminder_status(rid, 1)
        
        # Verify
        result = self.db.fetch_one("SELECT status FROM reminders WHERE id = ?", (rid,))
        assert result['status'] == 1
    
    def test_delete_reminder(self):
        """Test deleting a reminder."""
        self.crud.add_reminder("To Delete", "Cat", "2024-01-01")
        
        reminders = self.crud.get_reminders()
        rid = reminders[0]['id']
        
        self.crud.delete_reminder(rid)
        
        # Verify deleted
        result = self.db.fetch_one("SELECT * FROM reminders WHERE id = ?", (rid,))
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
