from database import Database

class PlannerAgent:
    """Agent responsible for breaking syllabus into milestones (topics)."""

    def __init__(self, db: Database):
        self.db = db

    def break_syllabus(self, subject_id):
        """Break the subject's syllabus into milestones."""
        # Get subject details
        subjects = self.db.get_subjects()
        subject = next((s for s in subjects if s[0] == subject_id), None)
        if not subject:
            raise ValueError(f"Subject with ID {subject_id} not found")

        # Check if milestones already exist
        existing_milestones = self.db.get_milestones(subject_id)
        if existing_milestones:
            return existing_milestones

        syllabus = subject[2]  # syllabus field
        topics = [t.strip() for t in syllabus.split(',') if t.strip()]

        # Simple logic: assign priorities based on position (first topics higher priority)
        milestones = []
        for i, topic in enumerate(topics):
            priority = 1 if i < len(topics) // 3 else (2 if i < 2 * len(topics) // 3 else 3)
            milestone_id = self.db.add_milestone(subject_id, topic, priority)
            milestones.append((milestone_id, topic, priority))

        return milestones