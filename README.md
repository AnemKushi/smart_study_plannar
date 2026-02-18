# Smart Study Planner

A lightweight Smart Study Planner using Agentic AI principles.

## Features

- Add subjects with syllabus, exam date, and daily study hours
- Automatically break syllabus into milestones and tasks
- Create daily/weekly schedules
- Track task completion
- Adaptive rescheduling for missed tasks
- Revision plan for high-priority topics

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the backend: `python src/main.py`
3. Open `static/index.html` in a browser for the frontend

## API Endpoints

- POST /subjects: Add a subject
- GET /subjects: Get all subjects
- POST /plan/{subject_id}: Create plan
- GET /plan/{subject_id}: Get plan
- PUT /tasks/{task_id}/complete: Mark task complete
- POST /adapt/{subject_id}: Adapt plan
- GET /revision/{subject_id}: Get revision plan

## Architecture

Uses 4 agents:
- Planner Agent: Breaks syllabus into milestones
- Task Agent: Converts milestones to tasks
- Scheduler Agent: Allocates time slots
- Adaptive Agent: Reschedules missed tasks

All data stored in SQLite, runs locally on 8GB RAM laptops.