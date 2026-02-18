import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import sqlite3
from database import Database
from planner import PlannerAgent
from task_agent import TaskAgent
from scheduler_agent import SchedulerAgent
from adaptive_agent import AdaptiveAgent

# Test database initialization and basic operations
def test_db():
    # Remove existing DB for clean test
    if os.path.exists('study_planner.db'):
        os.remove('study_planner.db')

    db = Database()
    # Add a test subject with syllabus
    subject_id = db.add_subject('Mathematics', 'Algebra,Calculus,Geometry,Statistics', '2026-05-01', 2.5)
    print(f"Added subject with ID: {subject_id}")

    # Test Planner Agent
    planner = PlannerAgent(db)
    milestones = planner.break_syllabus(subject_id)
    print("Milestones created:", milestones)

    # Test Task Agent
    task_agent = TaskAgent(db)
    tasks = task_agent.create_tasks(subject_id)
    print("Tasks created:", tasks)

    # Test Scheduler Agent
    scheduler = SchedulerAgent(db)
    schedules = scheduler.create_schedule(subject_id)
    print("Schedules created:", schedules)

    # Simulate missed tasks: mark Algebra and Calculus as not completed and set Algebra due to past
    db.update_task_completed(1, False)  # Algebra
    db.update_task_completed(2, False)  # Calculus
    # Set Algebra due to past date to simulate missed
    conn = sqlite3.connect('study_planner.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET due_date = ? WHERE id = ?', ('2026-02-17', 1))
    conn.commit()
    conn.close()

    # Test Adaptive Agent
    adaptive = AdaptiveAgent(db)
    rescheduled = adaptive.adapt_schedule(subject_id)
    print("Rescheduled tasks:", rescheduled)

    # Retrieve updated schedules
    schedules_db = db.get_schedules()
    print("Updated Schedules from DB:", schedules_db)

    # Retrieve updated tasks
    tasks_db = db.get_tasks()
    print("Updated Tasks from DB:", tasks_db)

    # Retrieve subjects
    subjects = db.get_subjects()
    print("Subjects:", subjects)

    # Retrieve milestones
    milestones_db = db.get_milestones(subject_id)
    print("Milestones from DB:", milestones_db)

    # Verify table creation
    conn = sqlite3.connect('study_planner.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables created:", tables)
    conn.close()

if __name__ == '__main__':
    test_db()