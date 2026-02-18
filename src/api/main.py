from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from database import Database
from planner import PlannerAgent
from task_agent import TaskAgent
from scheduler_agent import SchedulerAgent
from adaptive_agent import AdaptiveAgent

app = FastAPI(
    title="Smart Study Planner",
    description="Agentic AI Study Planner API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = Database()
planner = PlannerAgent(db)
task_agent = TaskAgent(db)
scheduler = SchedulerAgent(db)
adaptive = AdaptiveAgent(db)


@app.get("/")
def root():
    return {"message": "Smart Study Planner API", "status": "running"}


# -----------------------------
# SUBJECT MODEL
# -----------------------------
class SubjectInput(BaseModel):
    name: str
    syllabus: str  # Comma-separated topics
    exam_date: str  # YYYY-MM-DD
    daily_hours: float


# -----------------------------
# SUBJECT ROUTES
# -----------------------------
@app.post("/subjects")
def add_subject(subject: SubjectInput):
    subject_id = db.add_subject(
        subject.name,
        subject.syllabus,
        subject.exam_date,
        subject.daily_hours
    )
    return {"subject_id": subject_id, "message": "Subject added successfully"}


@app.get("/subjects")
def get_subjects():
    subjects = db.get_subjects()
    return {"subjects": subjects}


# -----------------------------
# CREATE STUDY PLAN
# -----------------------------
@app.post("/plan/{subject_id}")
def create_plan(subject_id: int):
    try:
        planner.break_syllabus(subject_id)
        task_agent.create_tasks(subject_id)
        scheduler.create_schedule(subject_id)

        milestones = db.get_milestones(subject_id)
        milestone_ids = [m[0] for m in milestones]

        tasks = [t for t in db.get_tasks() if t[1] in milestone_ids]
        task_ids = [t[0] for t in tasks]

        schedules = [s for s in db.get_schedules() if s[1] in task_ids]

        formatted_milestones = [
            {
                "id": m[0],
                "subject_id": m[1],
                "topic": m[2],
                "priority": ["High", "Medium", "Low"][m[3] - 1]
            }
            for m in milestones
        ]

        formatted_tasks = [
            {
                "id": t[0],
                "milestone_id": t[1],
                "description": t[2],
                "hours": t[3],
                "due_date": t[4],
                "completed": bool(t[5])
            }
            for t in tasks
        ]

        formatted_schedules = [
            {
                "id": s[0],
                "task_id": s[1],
                "date": s[2],
                "start_time": s[3],
                "end_time": s[4]
            }
            for s in schedules
        ]

        return {
            "milestones": formatted_milestones,
            "tasks": formatted_tasks,
            "schedules": formatted_schedules,
            "message": "Plan created successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -----------------------------
# GET STUDY PLAN
# -----------------------------
@app.get("/plan/{subject_id}")
def get_plan(subject_id: int):
    try:
        milestones = db.get_milestones(subject_id)
        milestone_ids = [m[0] for m in milestones]

        tasks = [t for t in db.get_tasks() if t[1] in milestone_ids]
        task_ids = [t[0] for t in tasks]

        schedules = [s for s in db.get_schedules() if s[1] in task_ids]

        formatted_milestones = [
            {
                "id": m[0],
                "subject_id": m[1],
                "topic": m[2],
                "priority": ["High", "Medium", "Low"][m[3] - 1]
            }
            for m in milestones
        ]

        formatted_tasks = [
            {
                "id": t[0],
                "milestone_id": t[1],
                "description": t[2],
                "hours": t[3],
                "due_date": t[4],
                "completed": bool(t[5])
            }
            for t in tasks
        ]

        formatted_schedules = [
            {
                "id": s[0],
                "task_id": s[1],
                "date": s[2],
                "start_time": s[3],
                "end_time": s[4]
            }
            for s in schedules
        ]

        return {
            "milestones": formatted_milestones,
            "tasks": formatted_tasks,
            "schedules": formatted_schedules
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# MARK TASK COMPLETE
# -----------------------------
@app.put("/tasks/{task_id}/complete")
def mark_task_complete(task_id: int, completed: bool = True):
    db.update_task_completed(task_id, completed)
    return {
        "message": f"Task {task_id} marked as {'completed' if completed else 'incomplete'}"
    }


# -----------------------------
# ADAPT PLAN
# -----------------------------
@app.post("/adapt/{subject_id}")
def adapt_plan(subject_id: int):
    try:
        rescheduled = adaptive.adapt_schedule(subject_id)
        return {
            "rescheduled": rescheduled,
            "message": "Plan adapted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# -----------------------------
# REVISION PLAN
# -----------------------------
@app.get("/revision/{subject_id}")
def get_revision_plan(subject_id: int):
    try:
        milestones = db.get_milestones(subject_id)
        high_priority = [m for m in milestones if m[3] == 1]

        revision_tasks = [
            {"topic": m[2], "priority": "High"}
            for m in high_priority
        ]

        return {"revision_plan": revision_tasks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# RESET DATABASE
# -----------------------------
@app.post("/reset")
def reset_database():
    try:
        import os
        if os.path.exists("study_planner.db"):
            os.remove("study_planner.db")

        # Reinitialize DB
        global db
        db = Database()

        return {"message": "Database reset successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)