from database import Database
from datetime import datetime, timedelta

class TaskAgent:
    """Agent responsible for converting milestones into daily tasks."""

    def __init__(self, db: Database):
        self.db = db

    def create_tasks(self, subject_id):
        """Create tasks from milestones for a subject."""
        # Get subject details
        subjects = self.db.get_subjects()
        subject = next((s for s in subjects if s[0] == subject_id), None)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")

        exam_date = datetime.fromisoformat(subject[3])  # exam_date
        daily_hours = subject[4]

        # Get milestones
        milestones = self.db.get_milestones(subject_id)

        # Check if tasks already exist for these milestones
        milestone_ids = [m[0] for m in milestones]
        existing_tasks = [t for t in self.db.get_tasks() if t[1] in milestone_ids]
        if existing_tasks:
            return existing_tasks

        tasks = []
        current_date = datetime.now().date()
        days_until_exam = (exam_date.date() - current_date).days

        # Simple logic: distribute tasks over available days
        total_milestones = len(milestones)
        days_available = max(1, days_until_exam // 7 * 7)  # Weekly basis, but simple

        for i, milestone in enumerate(milestones):
            milestone_id, _, topic, priority = milestone

            # Estimate hours based on priority (high=2h, med=1.5h, low=1h)
            est_hours = {1: 2.0, 2: 1.5, 3: 1.0}[priority]

            # Due date: spread over time, high priority sooner
            due_offset = (priority - 1) * (days_until_exam // 3)
            due_date = (current_date + timedelta(days=due_offset)).isoformat()

            description = f"Study {topic}"
            task_id = self.db.add_task(milestone_id, description, est_hours, due_date)
            tasks.append((task_id, description, est_hours, due_date))

        return tasks