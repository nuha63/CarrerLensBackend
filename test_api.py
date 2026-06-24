import requests
import json

url = "https://carrerlensbackend.onrender.com/api/job-match"
payload = {
    "job_title": "Software Engineer",
    "company": "Google",
    "industry": "IT",
    "resume_score": 0.8,
    "skills_match_score": 80.0,
    "experience_years": 2,
    "education_level": "Bachelor",
    "required_skills": ["Python", "Flutter"],
    "job_market_demand": "High"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
