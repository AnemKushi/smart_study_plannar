import sqlite3
from datetime import datetime

# Database helper class for CRUD operations
class Database:
    def __init__(self, db_path='study_planner.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with tables for subjects, milestones, tasks, schedules."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for subjects (user inputs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                syllabus TEXT NOT NULL,  -- Comma-separated topics
                exam_date TEXT NOT NULL,  -- ISO format YYYY-MM-DD
                daily_hours REAL NOT NULL
            )
        ''')

        # Table for milestones (broken-down syllabus topics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY,
                subject_id INTEGER,
                topic TEXT NOT NULL,
                priority INTEGER DEFAULT 1,  -- 1=high, 2=medium, 3=low
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        ''')

        # Table for tasks (daily study tasks)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                milestone_id INTEGER,
                description TEXT NOT NULL,
                estimated_hours REAL,
                due_date TEXT,  -- ISO format
                completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (milestone_id) REFERENCES milestones(id)
            )
        ''')

        # Table for schedules (daily/weekly plans)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY,
                task_id INTEGER,
                scheduled_date TEXT,  -- ISO format
                start_time TEXT,  -- HH:MM format
                end_time TEXT,  -- HH:MM format
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_subject(self, name, syllabus, exam_date, daily_hours):
        """Add a new subject."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subjects (name, syllabus, exam_date, daily_hours) VALUES (?, ?, ?, ?)',
                       (name, syllabus, exam_date, daily_hours))
        subject_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return subject_id

    def get_subjects(self):
        """Get all subjects."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM subjects')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_milestone(self, subject_id, topic, priority=1):
        """Add a milestone (topic) for a subject."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO milestones (subject_id, topic, priority) VALUES (?, ?, ?)',
                       (subject_id, topic, priority))
        milestone_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return milestone_id

    def get_milestones(self, subject_id):
        """Get milestones for a subject."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM milestones WHERE subject_id = ?', (subject_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_task(self, milestone_id, description, estimated_hours, due_date):
        """Add a task for a milestone."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (milestone_id, description, estimated_hours, due_date) VALUES (?, ?, ?, ?)',
                       (milestone_id, description, estimated_hours, due_date))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_tasks(self, milestone_id=None):
        """Get tasks, optionally for a specific milestone."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if milestone_id:
            cursor.execute('SELECT * FROM tasks WHERE milestone_id = ?', (milestone_id,))
        else:
            cursor.execute('SELECT * FROM tasks')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_schedule(self, task_id, scheduled_date, start_time, end_time):
        """Add a schedule entry for a task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO schedules (task_id, scheduled_date, start_time, end_time) VALUES (?, ?, ?, ?)',
                       (task_id, scheduled_date, start_time, end_time))
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id

    def get_schedules(self, task_id=None):
        """Get schedules, optionally for a specific task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if task_id:
            cursor.execute('SELECT * FROM schedules WHERE task_id = ?', (task_id,))
        else:
            cursor.execute('SELECT * FROM schedules')
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_task_completed(self, task_id, completed=True):
        """Mark a task as completed or not."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed, task_id))
        conn.commit()
        conn.close()