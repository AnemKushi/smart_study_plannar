from .database import Database
from datetime import datetime, timedelta
import sqlite3

class AdaptiveAgent:
    """Agent responsible for rescheduling tasks if they are missed."""

    def __init__(self, db: Database):
        self.db = db

    def adapt_schedule(self, subject_id):
        """Check for missed tasks and reschedule them."""
        # Get subject details
        subjects = self.db.get_subjects()
        subject = next((s for s in subjects if s[0] == subject_id), None)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")

        daily_hours = subject[4]
        exam_date = datetime.fromisoformat(subject[3]).date()
        current_date = datetime.now().date()

        # Get all tasks for the subject
        milestones = self.db.get_milestones(subject_id)
        milestone_ids = [m[0] for m in milestones]
        tasks = [t for t in self.db.get_tasks() if t[1] in milestone_ids]

        rescheduled = []
        for task in tasks:
            task_id, _, description, est_hours, due_date, completed = task
            due = datetime.fromisoformat(due_date).date()

            if not completed and current_date > due:
                # Task is missed, reschedule to next available day
                new_due = current_date + timedelta(days=1)
                while new_due <= exam_date:
                    # Check if we can schedule on this day
                    day_schedules = [s for s in self.db.get_schedules() if s[2] == new_due.isoformat()]
                    used_hours = sum((datetime.strptime(s[4], '%H:%M') - datetime.strptime(s[3], '%H:%M')).seconds / 3600 for s in day_schedules)

                    if used_hours + est_hours <= daily_hours:
                        # Reschedule: update due_date and add new schedule
                        conn = sqlite3.connect(self.db.db_path)
                        cursor = conn.cursor()
                        cursor.execute('UPDATE tasks SET due_date = ? WHERE id = ?', (new_due.isoformat(), task_id))
                        conn.commit()
                        conn.close()

                        # Add new schedule (simple: start after existing)
                        start_time = '09:00' if not day_schedules else day_schedules[-1][4]  # end of last
                        start_dt = datetime.strptime(start_time, '%H:%M')
                        end_dt = start_dt + timedelta(hours=est_hours)
                        end_time = end_dt.strftime('%H:%M')

                        schedule_id = self.db.add_schedule(task_id, new_due.isoformat(), start_time, end_time)
                        rescheduled.append((task_id, new_due.isoformat(), start_time, end_time))
                        break
                    else:
                        new_due += timedelta(days=1)

        return rescheduled