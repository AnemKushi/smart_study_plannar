import requests
import os

# Remove existing DB for clean test
if os.path.exists('study_planner.db'):
    os.remove('study_planner.db')

# Test script to add subject and create plan
API_BASE = 'http://127.0.0.1:8000'

# Add subject
subject_data = {
    "name": "Mathematics",
    "syllabus": "Algebra,Calculus,Geometry,Statistics",
    "exam_date": "2026-05-01",
    "daily_hours": 2.5
}
response = requests.post(f"{API_BASE}/subjects", json=subject_data)
print("Add subject:", response.json())

subject_id = response.json()['subject_id']

# Create plan
response = requests.post(f"{API_BASE}/plan/{subject_id}")
print("Create plan:", response.json())

# Get plan
response = requests.get(f"{API_BASE}/plan/{subject_id}")
print("Get plan:", response.json())