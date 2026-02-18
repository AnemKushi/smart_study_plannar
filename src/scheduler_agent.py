from database import Database
from datetime import datetime, timedelta, time

class SchedulerAgent:
    """Agent responsible for allocating time to tasks based on priority and exam date."""

    def __init__(self, db: Database):
        self.db = db

    def create_schedule(self, subject_id):
        """Create daily schedules for tasks of a subject."""
        # Get subject details
        subjects = self.db.get_subjects()
        subject = next((s for s in subjects if s[0] == subject_id), None)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")

        daily_hours = subject[4]
        exam_date = datetime.fromisoformat(subject[3]).date()

        # Get tasks for the subject
        milestones = self.db.get_milestones(subject_id)
        milestone_ids = [m[0] for m in milestones]
        tasks = [t for t in self.db.get_tasks() if t[1] in milestone_ids]  # t[1] is milestone_id
        # Check if schedules already exist for these tasks
        task_ids = [t[0] for t in tasks]
        existing_schedules = [s for s in self.db.get_schedules() if s[1] in task_ids]
        if existing_schedules:
            return existing_schedules
        # Sort tasks by priority (from milestones) and due date
        task_priorities = {m[0]: m[3] for m in milestones}  # milestone_id: priority
        tasks.sort(key=lambda t: (task_priorities[t[1]], t[4]))  # priority, due_date

        # Simple scheduling: start from today, allocate daily up to daily_hours
        current_date = datetime.now().date()
        schedule_entries = []

        day_start = time(9, 0)  # Assume study starts at 9 AM
        for task in tasks:
            task_id, _, description, est_hours, due_date, _ = task
            due = datetime.fromisoformat(due_date).date()

            # Schedule on the earliest available day before due date
            scheduled_date = current_date
            while scheduled_date <= due:
                # Check available hours on this day
                day_schedules = [s for s in self.db.get_schedules() if s[2] == scheduled_date.isoformat()]
                used_hours = sum((datetime.strptime(s[4], '%H:%M') - datetime.strptime(s[3], '%H:%M')).seconds / 3600 for s in day_schedules)

                if used_hours + est_hours <= daily_hours:
                    # Schedule it
                    start_time = day_start.replace(hour=int(day_start.hour + used_hours))
                    end_time = start_time.replace(hour=int(start_time.hour + est_hours))
                    schedule_id = self.db.add_schedule(task_id, scheduled_date.isoformat(), start_time.strftime('%H:%M'), end_time.strftime('%H:%M'))
                    schedule_entries.append((schedule_id, scheduled_date.isoformat(), start_time.strftime('%H:%M'), end_time.strftime('%H:%M')))
                    break
                else:
                    scheduled_date += timedelta(days=1)

        return schedule_entries