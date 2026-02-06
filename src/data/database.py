
import sqlite3
import os

class DatabaseManager:
    DB_NAME = "estudei.db"

    def __init__(self):
        # Ensure we are saving in the project root or app data
        self.conn = None
        self.init_db()

    def get_connection(self):
        if not self.conn:
             self.conn = sqlite3.connect(self.DB_NAME, check_same_thread=False)
             # return rows as dictionaries
             self.conn.row_factory = sqlite3.Row 
        return self.conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Subjects Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                total_topics INTEGER DEFAULT 0,
                completed_topics INTEGER DEFAULT 0,
                weight REAL DEFAULT 1.0,
                color TEXT DEFAULT '#00bfa5'
            )
        ''')

        # Study Sessions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                topic TEXT,
                date TEXT, -- ISO8601 string YYYY-MM-DD HH:MM:SS
                duration_seconds INTEGER,
                type TEXT, -- 'TEORIA', 'QUESTOES', 'REVISAO'
                questions_correct INTEGER DEFAULT 0,
                questions_wrong INTEGER DEFAULT 0,
                pages_start INTEGER DEFAULT 0,
                pages_end INTEGER DEFAULT 0,
                video_start TEXT,
                video_end TEXT,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        ''')
        
        # Mock Exams Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mock_exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                date TEXT,
                score REAL,
                total_questions INTEGER,
                time_spent TEXT,
                style TEXT,
                board TEXT
            )
        ''')
        
        # Mock Exam Items (Per-Subject Breakdown)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mock_exam_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mock_exam_id INTEGER,
                subject_id INTEGER,
                weight REAL DEFAULT 1.0,
                correct INTEGER DEFAULT 0,
                wrong INTEGER DEFAULT 0,
                blank INTEGER DEFAULT 0,
                FOREIGN KEY(mock_exam_id) REFERENCES mock_exams(id),
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        ''')
        
        # ... (skipping unchanged tables) ...

        # Topics Table (Detailed Syllabus)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                title TEXT,
                completed INTEGER DEFAULT 0, -- Boolean
                order_index INTEGER DEFAULT 0,
                material_link TEXT,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
            )
        ''')
        # Reminders Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                category TEXT,
                date_time TEXT,
                status INTEGER DEFAULT 0 -- 0=Pending, 1=Done, 2=Ignored
            )
        ''')

        # Plans Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                observations TEXT,
                has_image BOOLEAN DEFAULT 0,
                is_generic BOOLEAN DEFAULT 0, -- "Não estou estudando para prova específica"
                is_archived BOOLEAN DEFAULT 0,
                created_at TEXT
            )
        ''')

        # Plan-Subjects Association Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plan_subjects (
                plan_id INTEGER,
                subject_id INTEGER,
                FOREIGN KEY(plan_id) REFERENCES plans(id),
                FOREIGN KEY(subject_id) REFERENCES subjects(id),
                PRIMARY KEY (plan_id, subject_id)
            )
        ''')

        # --- Schema Migrations ---
        # Add 'status' column to reminders if missing (migration from old schema)
        cursor.execute("PRAGMA table_info(reminders)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'status' not in columns:
            cursor.execute("ALTER TABLE reminders ADD COLUMN status INTEGER DEFAULT 0")
            print("Migration: Added 'status' column to reminders table.")
        
        # Add 'style' and 'board' columns to mock_exams if missing
        cursor.execute("PRAGMA table_info(mock_exams)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'style' not in columns:
            cursor.execute("ALTER TABLE mock_exams ADD COLUMN style TEXT")
            print("Migration: Added 'style' column to mock_exams table.")
        if 'board' not in columns:
            cursor.execute("ALTER TABLE mock_exams ADD COLUMN board TEXT")
            print("Migration: Added 'board' column to mock_exams table.")
        
        # Add study_sessions columns if missing
        cursor.execute("PRAGMA table_info(study_sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'pages_start' not in columns:
            cursor.execute("ALTER TABLE study_sessions ADD COLUMN pages_start INTEGER DEFAULT 0")
            print("Migration: Added 'pages_start' column to study_sessions table.")
        if 'pages_end' not in columns:
            cursor.execute("ALTER TABLE study_sessions ADD COLUMN pages_end INTEGER DEFAULT 0")
            print("Migration: Added 'pages_end' column to study_sessions table.")
        if 'video_start' not in columns:
            cursor.execute("ALTER TABLE study_sessions ADD COLUMN video_start TEXT")
            print("Migration: Added 'video_start' column to study_sessions table.")
        if 'video_end' not in columns:
            cursor.execute("ALTER TABLE study_sessions ADD COLUMN video_end TEXT")
            print("Migration: Added 'video_end' column to study_sessions table.")

        # Initial Seed Data (if empty)
        cursor.execute("SELECT count(*) FROM subjects")
        if cursor.fetchone()[0] == 0:
            self.seed_data(cursor)
        
        conn.commit()

    def seed_data(self, cursor):
        subjects = [
            ("Administração Financeira e Orçamentária", "Administração", 120, 10),
            ("Auditoria do Setor Público", "Auditoria", 80, 5),
            ("Controle Externo e Legislação Institucional", "Direito", 60, 20),
            ("Direito Administrativo", "Direito", 150, 45),
            ("Direito Constitucional", "Direito", 100, 30),
            ("Português", "Básicas", 200, 100),
            ("Informática", "Básicas", 50, 5)
        ]
        cursor.executemany("INSERT INTO subjects (name, category, total_topics, completed_topics) VALUES (?, ?, ?, ?)", subjects)
        print("Database seeded with initial subjects.")

    def execute_query(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

# Singleton instance
db = DatabaseManager()
