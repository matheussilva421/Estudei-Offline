
from src.data.database import db
from datetime import datetime, timedelta

# --- Subjects ---
def get_all_subjects():
    return db.fetch_all("SELECT * FROM subjects ORDER BY name")

def get_subject_progress(subject_id):
    # This assumes we will have a topics table later, effectively using columns for now
    sub = db.fetch_one("SELECT * FROM subjects WHERE id = ?", (subject_id,))
    if sub:
        return (sub['completed_topics'] / sub['total_topics']) if sub['total_topics'] > 0 else 0
    return 0

# --- Study Sessions ---
def add_study_session(subject_id, topic, duration_seconds, type_label, correct=0, wrong=0, date=None, pages_start=0, pages_end=0, video_start="", video_end=""):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db.execute_query('''
        INSERT INTO study_sessions (subject_id, topic, date, duration_seconds, type, questions_correct, questions_wrong, pages_start, pages_end, video_start, video_end)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (subject_id, topic, date, duration_seconds, type_label, correct, wrong, pages_start, pages_end, video_start, video_end))


def get_recent_sessions(limit=5):
    return db.fetch_all('''
        SELECT s.name as subject_name, ss.* 
        FROM study_sessions ss
        JOIN subjects s ON ss.subject_id = s.id
        ORDER BY ss.date DESC
        LIMIT ?
    ''', (limit,))

def get_total_study_time():
    res = db.fetch_one("SELECT SUM(duration_seconds) as total FROM study_sessions")
    return res['total'] if res['total'] else 0

def get_weekly_study_data():
    """
    Returns data for the Current Week (Mon-Sun).
    Aggregates study time per day.
    """
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Initialize all days with 0
    data = {}
    days_labels = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        data[day_date] = 0.0

    # Optimized Query: Group By Date
    # Note: SQLite 'date(date)' might depend on how date is stored. 
    # We store as 'YYYY-MM-DD HH:MM:SS'. so date(date) works.
    rows = db.fetch_all('''
        SELECT date(date) as day, SUM(duration_seconds) as total_seconds
        FROM study_sessions
        WHERE date(date) >= ?
        GROUP BY day
    ''', (start_of_week.isoformat(),))
    
    for r in rows:
        try:
            d_obj = datetime.strptime(r['day'], "%Y-%m-%d").date()
            if d_obj in data:
                data[d_obj] = (r['total_seconds'] or 0) / 3600.0
        except ValueError:
            pass
            
    # Convert to list of tuples for UI
    result = []
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        result.append((days_labels[i], data[day_date]))
        
    return result

def get_performance_stats():
    res = db.fetch_one('''
        SELECT SUM(questions_correct) as correct, SUM(questions_wrong) as wrong
        FROM study_sessions
    ''')
    c = res['correct'] if res['correct'] else 0
    w = res['wrong'] if res['wrong'] else 0
    return calculate_performance(c, w), c, w

def calculate_performance(correct, wrong):
    """Calculate performance percentage."""
    total = correct + wrong
    return int((correct / total) * 100) if total > 0 else 0

def get_subject_stats(subject_id):
    """Return aggregated stats for a subject."""
    return db.fetch_one('''
        SELECT
            COALESCE(SUM(duration_seconds), 0) as total_seconds,
            COALESCE(SUM(questions_correct), 0) as total_correct,
            COALESCE(SUM(questions_wrong), 0) as total_wrong,
            COALESCE(SUM(CASE WHEN pages_end >= pages_start THEN pages_end - pages_start ELSE 0 END), 0) as total_pages
        FROM study_sessions
        WHERE subject_id = ?
    ''', (subject_id,))

def get_history_stats():
    """Return global stats for history page indicators."""
    return db.fetch_one('''
        SELECT
            COALESCE(SUM(duration_seconds), 0) as total_seconds,
            COALESCE(SUM(questions_correct), 0) as total_correct,
            COALESCE(SUM(questions_wrong), 0) as total_wrong,
            COALESCE(SUM(CASE WHEN pages_end >= pages_start THEN pages_end - pages_start ELSE 0 END), 0) as total_pages
        FROM study_sessions
    ''')

def get_topics_stats():
    """Return global topics completion stats."""
    return db.fetch_one('''
        SELECT
            COALESCE(SUM(total_topics), 0) as total_topics,
            COALESCE(SUM(completed_topics), 0) as completed_topics
        FROM subjects
    ''')

def get_subject_stats(subject_id):
    """Return aggregated stats for a subject."""
    return db.fetch_one('''
        SELECT
            COALESCE(SUM(duration_seconds), 0) as total_seconds,
            COALESCE(SUM(questions_correct), 0) as total_correct,
            COALESCE(SUM(questions_wrong), 0) as total_wrong,
            COALESCE(SUM(pages_end - pages_start), 0) as total_pages
        FROM study_sessions
        WHERE subject_id = ?
    ''', (subject_id,))

def get_history_stats():
    """Return global stats for history page indicators."""
    return db.fetch_one('''
        SELECT
            COALESCE(SUM(duration_seconds), 0) as total_seconds,
            COALESCE(SUM(questions_correct), 0) as total_correct,
            COALESCE(SUM(questions_wrong), 0) as total_wrong,
            COALESCE(SUM(pages_end - pages_start), 0) as total_pages
        FROM study_sessions
    ''')

def get_topics_stats():
    """Return global topics completion stats."""
    return db.fetch_one('''
        SELECT
            COALESCE(SUM(total_topics), 0) as total_topics,
            COALESCE(SUM(completed_topics), 0) as completed_topics
        FROM subjects
    ''')

# --- Mock Exams ---
def add_mock_exam(name, date, score, total, time_spent):
    db.execute_query("INSERT INTO mock_exams (name, date, score, total_questions, time_spent) VALUES (?, ?, ?, ?, ?)",
                     (name, date, score, total, time_spent))

def add_mock_exam_items_bulk(exam_id, items_data):
    # items_data = [(subject_id, weight, correct, wrong, blank), ...]
    data = [(exam_id, *item) for item in items_data]
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO mock_exam_items (mock_exam_id, subject_id, weight, correct, wrong, blank)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()

def get_mock_exams():
    return db.fetch_all("SELECT * FROM mock_exams ORDER BY date DESC")

# --- Topics (Syllabus) ---
def add_topics_bulk(subject_id, topics_list):
    # topics_list is a list of strings
    data = [(subject_id, t, 0, i) for i, t in enumerate(topics_list)]
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO topics (subject_id, title, completed, order_index) VALUES (?, ?, ?, ?)", data)
    conn.commit()

def get_topics_by_subject(subject_id):
    return db.fetch_all("SELECT * FROM topics WHERE subject_id = ? ORDER BY order_index", (subject_id,))

def toggle_topic_complete(topic_id, completed):
    val = 1 if completed else 0
    db.execute_query("UPDATE topics SET completed = ? WHERE id = ?", (val, topic_id))
    
    # Update subject stats
    # Get subject_id
    t = db.fetch_one("SELECT subject_id FROM topics WHERE id = ?", (topic_id,))
    if t:
        sub_id = t['subject_id']
        # Count total and completed
        res = db.fetch_one("SELECT COUNT(*) as total, SUM(completed) as done FROM topics WHERE subject_id = ?", (sub_id,))
        total = res['total']
        done = res['done'] if res['done'] else 0
        
        db.execute_query("UPDATE subjects SET total_topics = ?, completed_topics = ? WHERE id = ?", (total, done, sub_id))


# --- Reminders ---
def add_reminder(content, category, date_time):
    db.execute_query("INSERT INTO reminders (content, category, date_time) VALUES (?, ?, ?)", 
                     (content, category, date_time))

def get_reminders(limit=5):
    return db.fetch_all("SELECT * FROM reminders WHERE status = 0 ORDER BY date_time ASC LIMIT ?", (limit,))

def delete_reminder(reminder_id):
    db.execute_query("DELETE FROM reminders WHERE id = ?", (reminder_id,))

# --- Plans ---
def add_plan(name, obs, has_image=False, is_generic=False, subject_ids=None):
    """Create a new plan and optionally associate subjects."""
    if subject_ids is None:
        subject_ids = []
    
    date = datetime.now().isoformat()
    cursor = db.execute_query(
        "INSERT INTO plans (name, observations, has_image, is_generic, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, obs, has_image, is_generic, date)
    )
    plan_id = cursor.lastrowid
    
    # Associate subjects (optimized bulk insert)
    if subject_ids:
        data = [(plan_id, sid) for sid in subject_ids]
        conn = db.get_connection()
        conn.cursor().executemany("INSERT INTO plan_subjects (plan_id, subject_id) VALUES (?, ?)", data)
        conn.commit()
    
    return plan_id

def get_plans(archived=0):
    # TODO: Fetch subjects count or names if needed
    return db.fetch_all("SELECT * FROM plans WHERE is_archived = ? ORDER BY created_at DESC", (archived,))

def archive_plan(plan_id):
    db.execute_query("UPDATE plans SET is_archived = 1 WHERE id = ?", (plan_id,))

# --- Reviews (via Reminders) ---
def get_reviews():
    # Return all reminders with category 'Revisão'
    return db.fetch_all("SELECT * FROM reminders WHERE category = 'Revisão' ORDER BY date_time ASC")

def update_reminder_status(rid, status):
    # status: 0=Pending, 1=Done, 2=Ignored
    db.execute_query("UPDATE reminders SET status = ? WHERE id = ?", (status, rid))

# --- Plan Extensions ---
def get_plan_by_id(plan_id):
    return db.fetch_one("SELECT * FROM plans WHERE id = ?", (plan_id,))

def get_subjects_by_plan(plan_id):
    # Retrieve subjects linked to this plan
    return db.fetch_all('''
        SELECT s.* 
        FROM subjects s
        JOIN plan_subjects ps ON s.id = ps.subject_id
        WHERE ps.plan_id = ?
    ''', (plan_id,))

# --- Subjects (Extended) ---
def add_subject_return_id(name, category, color):
    # Check if exists by name?
    # For now, simplistic insert
    cursor = db.execute_query("INSERT INTO subjects (name, category, color) VALUES (?, ?, ?)", (name, category, color))
    return cursor.lastrowid

def add_subject_to_plan(plan_id, subject_id):
    """Link a subject to a plan, ignoring if already linked."""
    import sqlite3
    try:
        db.execute_query("INSERT INTO plan_subjects (plan_id, subject_id) VALUES (?, ?)", (plan_id, subject_id))
    except sqlite3.IntegrityError:
        pass  # Already linked (PRIMARY KEY constraint)

def update_subject_details(subject_id, name, color):
    db.execute_query("UPDATE subjects SET name = ?, color = ? WHERE id = ?", (name, color, subject_id))

def remove_subject_from_plan(plan_id, subject_id):
    db.execute_query("DELETE FROM plan_subjects WHERE plan_id = ? AND subject_id = ?", (plan_id, subject_id))

# --- Topic Management ---
def add_topic(subject_id, title, material_link=""):
    # Get max order
    res = db.fetch_one("SELECT MAX(order_index) as max_idx FROM topics WHERE subject_id = ?", (subject_id,))
    idx = (res['max_idx'] + 1) if res['max_idx'] is not None else 0
    
    db.execute_query("INSERT INTO topics (subject_id, title, order_index, material_link) VALUES (?, ?, ?, ?)", (subject_id, title, idx, material_link))
    _update_subject_stats(subject_id)

def update_topic(topic_id, title=None, material_link=None):
    if title is not None and material_link is not None:
         db.execute_query("UPDATE topics SET title = ?, material_link = ? WHERE id = ?", (title, material_link, topic_id))
    elif title is not None:
         db.execute_query("UPDATE topics SET title = ? WHERE id = ?", (title, topic_id))
    elif material_link is not None:
         db.execute_query("UPDATE topics SET material_link = ? WHERE id = ?", (material_link, topic_id))

def delete_topic(topic_id):
    # Get sub id before delete for stats
    t = db.fetch_one("SELECT subject_id FROM topics WHERE id = ?", (topic_id,))
    if t:
        db.execute_query("DELETE FROM topics WHERE id = ?", (topic_id,))
        _update_subject_stats(t['subject_id'])

def _update_subject_stats(subject_id):
    res = db.fetch_one("SELECT COUNT(*) as total, SUM(completed) as done FROM topics WHERE subject_id = ?", (subject_id,))
    total = res['total']
    done = res['done'] if res['done'] else 0
    db.execute_query("UPDATE subjects SET total_topics = ?, completed_topics = ? WHERE id = ?", (total, done, subject_id))

# --- Utility Functions (Added) ---
def get_subject_by_id(subject_id):
    """Retrieve a single subject by ID."""
    return db.fetch_one("SELECT * FROM subjects WHERE id = ?", (subject_id,))

def delete_study_session(session_id):
    """Delete a study session by ID."""
    db.execute_query("DELETE FROM study_sessions WHERE id = ?", (session_id,))

def delete_subject(subject_id):
    """Delete a subject and related records."""
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN")
        cursor.execute("DELETE FROM mock_exam_items WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM study_sessions WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM topics WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM plan_subjects WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def get_mock_exam_items(exam_id):
    """Get all items (per-subject breakdown) for a mock exam."""
    return db.fetch_all('''
        SELECT mei.*, s.name as subject_name 
        FROM mock_exam_items mei
        JOIN subjects s ON mei.subject_id = s.id
        WHERE mei.mock_exam_id = ?
    ''', (exam_id,))

def delete_mock_exam(exam_id):
    """Delete a mock exam and all its items."""
    db.execute_query("DELETE FROM mock_exam_items WHERE mock_exam_id = ?", (exam_id,))
    db.execute_query("DELETE FROM mock_exams WHERE id = ?", (exam_id,))

def get_study_sessions_by_subject(subject_id):
    """Get all study sessions for a specific subject."""
    return db.fetch_all('''
        SELECT * FROM study_sessions 
        WHERE subject_id = ? 
        ORDER BY date DESC
    ''', (subject_id,))

def get_all_study_sessions():
    """Get all study sessions with subject names."""
    return db.fetch_all('''
        SELECT ss.*, s.name as subject_name 
        FROM study_sessions ss 
        JOIN subjects s ON ss.subject_id = s.id 
        ORDER BY ss.date DESC
    ''')


# ============================================================================
# OPTIMIZED BATCH QUERIES (Eliminate N+1 Patterns)
# ============================================================================

def get_plans_with_subject_count(archived=0):
    """
    Get all plans with subject count in a SINGLE query.
    Eliminates N+1 when listing plans with subject count.
    """
    return db.fetch_all('''
        SELECT p.*, COUNT(ps.subject_id) as subject_count
        FROM plans p
        LEFT JOIN plan_subjects ps ON p.id = ps.plan_id
        WHERE p.is_archived = ?
        GROUP BY p.id
        ORDER BY p.created_at DESC
    ''', (archived,))


def get_all_plans_with_subjects(archived=0):
    """
    Get all plans with their subjects loaded in TWO queries (not N+1).
    Returns: {plan_id: {plan_data, subjects: [...]}}
    """
    # Query 1: Get all plans
    plans = db.fetch_all('''
        SELECT * FROM plans WHERE is_archived = ? ORDER BY created_at DESC
    ''', (archived,))
    
    if not plans:
        return []
    
    plan_ids = [p['id'] for p in plans]
    placeholders = ','.join('?' * len(plan_ids))
    
    # Query 2: Get all subjects for all plans at once
    subjects = db.fetch_all(f'''
        SELECT ps.plan_id, s.*
        FROM plan_subjects ps
        JOIN subjects s ON ps.subject_id = s.id
        WHERE ps.plan_id IN ({placeholders})
    ''', tuple(plan_ids))
    
    # Group subjects by plan_id
    plan_subjects = {}
    for s in subjects:
        pid = s['plan_id']
        if pid not in plan_subjects:
            plan_subjects[pid] = []
        plan_subjects[pid].append(dict(s))
    
    # Merge into results
    result = []
    for p in plans:
        plan_dict = dict(p)
        plan_dict['subjects'] = plan_subjects.get(p['id'], [])
        result.append(plan_dict)
    
    return result


def get_subjects_with_stats():
    """
    Get all subjects with aggregated study stats in a SINGLE query.
    Eliminates N+1 when building subject cards with time/performance.
    """
    return db.fetch_all('''
        SELECT 
            s.*,
            COALESCE(SUM(ss.duration_seconds), 0) as total_study_seconds,
            COALESCE(SUM(ss.questions_correct), 0) as total_correct,
            COALESCE(SUM(ss.questions_wrong), 0) as total_wrong,
            COUNT(ss.id) as session_count
        FROM subjects s
        LEFT JOIN study_sessions ss ON s.id = ss.subject_id
        GROUP BY s.id
        ORDER BY s.name
    ''')


def get_dashboard_stats():
    """
    Get all dashboard statistics in a SINGLE query.
    Returns total time, performance, session count.
    """
    return db.fetch_one('''
        SELECT 
            COALESCE(SUM(duration_seconds), 0) as total_seconds,
            COALESCE(SUM(questions_correct), 0) as total_correct,
            COALESCE(SUM(questions_wrong), 0) as total_wrong,
            COUNT(*) as session_count
        FROM study_sessions
    ''')


def get_mock_exams_with_stats():
    """
    Get all mock exams with aggregated item stats in a SINGLE query.
    """
    return db.fetch_all('''
        SELECT 
            me.*,
            COALESCE(SUM(mei.correct), 0) as total_correct,
            COALESCE(SUM(mei.wrong), 0) as total_wrong,
            COALESCE(SUM(mei.blank), 0) as total_blank,
            COUNT(mei.id) as subject_count
        FROM mock_exams me
        LEFT JOIN mock_exam_items mei ON me.id = mei.mock_exam_id
        GROUP BY me.id
        ORDER BY me.date DESC
    ''')


def get_reviews_grouped():
    """
    Get all reviews grouped by status in a SINGLE query.
    Returns: {status_code: [reminders]}
    """
    rows = db.fetch_all('''
        SELECT * FROM reminders 
        WHERE category = 'Revisão' 
        ORDER BY status, date_time ASC
    ''')
    
    grouped = {0: [], 1: [], 2: []}  # 0=Pending, 1=Done, 2=Ignored
    for r in rows:
        status = r['status'] or 0
        if status in grouped:
            grouped[status].append(dict(r))
    
    return grouped
