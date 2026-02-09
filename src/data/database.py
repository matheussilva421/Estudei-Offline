
import sqlite3
import threading
import atexit


class DatabaseManager:
    """
    Thread-safe SQLite database manager.
    Uses thread-local connections to ensure each thread has its own connection.
    Implements proper connection lifecycle management.
    """
    
    DB_NAME = "estudei.db"

    def __init__(self):
        # Thread-local storage for connections
        self._local = threading.local()
        # Lock for schema initialization (one-time setup)
        self._init_lock = threading.Lock()
        self._initialized = False
        # Track all connections for cleanup
        self._connections = []
        self._connections_lock = threading.Lock()
        
        # Register cleanup on exit
        atexit.register(self.close_all)
        
        # Initialize schema (thread-safe)
        self.init_db()

    def get_connection(self):
        """
        Get a thread-local database connection.
        Each thread gets its own connection (thread-safe).
        """
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            conn = sqlite3.connect(self.DB_NAME, timeout=30.0)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=30000")
            self._local.conn = conn
            
            # Track connection for cleanup
            with self._connections_lock:
                self._connections.append(conn)
        
        return self._local.conn

    def close_connection(self):
        """Close the current thread's connection."""
        if hasattr(self._local, 'conn') and self._local.conn:
            try:
                self._local.conn.close()
            except Exception:
                pass
            finally:
                with self._connections_lock:
                    if self._local.conn in self._connections:
                        self._connections.remove(self._local.conn)
                self._local.conn = None

    def close_all(self):
        """Close all tracked connections (called on exit)."""
        with self._connections_lock:
            for conn in self._connections:
                try:
                    conn.close()
                except Exception:
                    pass
            self._connections.clear()

    def init_db(self):
        """Initialize database schema (thread-safe, runs once)."""
        with self._init_lock:
            if self._initialized:
                return
            
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
                    date TEXT,
                    duration_seconds INTEGER,
                    type TEXT,
                    questions_correct INTEGER DEFAULT 0,
                    questions_wrong INTEGER DEFAULT 0,
                    pages_start INTEGER DEFAULT 0,
                    pages_end INTEGER DEFAULT 0,
                    video_start TEXT,
                    video_end TEXT,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
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
            
            # Mock Exam Items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mock_exam_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mock_exam_id INTEGER,
                    subject_id INTEGER,
                    weight REAL DEFAULT 1.0,
                    correct INTEGER DEFAULT 0,
                    wrong INTEGER DEFAULT 0,
                    blank INTEGER DEFAULT 0,
                    FOREIGN KEY(mock_exam_id) REFERENCES mock_exams(id) ON DELETE CASCADE,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                )
            ''')

            # Topics Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER,
                    title TEXT,
                    completed INTEGER DEFAULT 0,
                    order_index INTEGER DEFAULT 0,
                    material_link TEXT,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
                )
            ''')
            
            # Reminders Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    category TEXT,
                    date_time TEXT,
                    status INTEGER DEFAULT 0
                )
            ''')

            # Plans Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    observations TEXT,
                    has_image BOOLEAN DEFAULT 0,
                    is_generic BOOLEAN DEFAULT 0,
                    is_archived BOOLEAN DEFAULT 0,
                    created_at TEXT
                )
            ''')

            # Plan-Subjects Association Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plan_subjects (
                    plan_id INTEGER,
                    subject_id INTEGER,
                    FOREIGN KEY(plan_id) REFERENCES plans(id) ON DELETE CASCADE,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                    PRIMARY KEY (plan_id, subject_id)
                )
            ''')

            # --- Schema Migrations ---
            self._run_migrations(cursor)

            # Initial Seed Data (if empty)
            cursor.execute("SELECT count(*) FROM subjects")
            if cursor.fetchone()[0] == 0:
                self.seed_data(cursor)
            
            conn.commit()
            self._initialized = True

    def _run_migrations(self, cursor):
        """Run schema migrations for backwards compatibility."""
        # Reminders: add status column
        cursor.execute("PRAGMA table_info(reminders)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'status' not in columns:
            cursor.execute("ALTER TABLE reminders ADD COLUMN status INTEGER DEFAULT 0")
            print("Migration: Added 'status' column to reminders table.")
        
        # Mock exams: add style and board columns
        cursor.execute("PRAGMA table_info(mock_exams)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'style' not in columns:
            cursor.execute("ALTER TABLE mock_exams ADD COLUMN style TEXT")
            print("Migration: Added 'style' column to mock_exams table.")
        if 'board' not in columns:
            cursor.execute("ALTER TABLE mock_exams ADD COLUMN board TEXT")
            print("Migration: Added 'board' column to mock_exams table.")
        
        # Study sessions: add pages and video columns
        cursor.execute("PRAGMA table_info(study_sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        for col_name, col_def in [
            ('pages_start', 'INTEGER DEFAULT 0'),
            ('pages_end', 'INTEGER DEFAULT 0'),
            ('video_start', 'TEXT'),
            ('video_end', 'TEXT')
        ]:
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE study_sessions ADD COLUMN {col_name} {col_def}")
                print(f"Migration: Added '{col_name}' column to study_sessions table.")

    def seed_data(self, cursor):
        """Insert initial seed data."""
        subjects = [
            ("Administração Financeira e Orçamentária", "Administração", 120, 10),
            ("Auditoria do Setor Público", "Auditoria", 80, 5),
            ("Controle Externo e Legislação Institucional", "Direito", 60, 20),
            ("Direito Administrativo", "Direito", 150, 45),
            ("Direito Constitucional", "Direito", 100, 30),
            ("Português", "Básicas", 200, 100),
            ("Informática", "Básicas", 50, 5)
        ]
        cursor.executemany(
            "INSERT INTO subjects (name, category, total_topics, completed_topics) VALUES (?, ?, ?, ?)",
            subjects
        )
        print("Database seeded with initial subjects.")

    def execute_query(self, query, params=()):
        """Execute a write query with automatic commit."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            conn.rollback()
            raise e

    def fetch_all(self, query, params=()):
        """Execute a read query and return all results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=()):
        """Execute a read query and return one result."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


# Singleton instance
db = DatabaseManager()
