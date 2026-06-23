"""
ML Training & Integration Quickstart Guide

🚀 Quick Start - 5 Minutes to ML Predictions!
=====================================================

Step 1: Train the Models
------------------------
cd career_lens_backend
python -m app.ml_pipeline.train_models

This will:
✅ Load your datasets (resume data + jobs data)
✅ Run exploratory analysis
✅ Train 4 ML models (resume scorer, job matcher, salary predictor, skill gap analyzer)
✅ Save trained models to: app/trained_models/

Step 2: Start the Backend
------------------------
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --env-file .env

You should see:
✅ Uvicorn running on http://0.0.0.0:8001
✅ All models loaded successfully!

Step 3: Test ML API Endpoints
-----------------------------

Option A: Using Swagger UI (Visual)
1. Open: http://localhost:8001/docs
2. Click on endpoints under "ML Analysis" section
3. Click "Try it out" and test with sample data

Option B: Using cURL (Terminal)

1. Analyze Resume:
curl -X POST "http://localhost:8001/api/analyze-resume" \
  -H "Content-Type: application/json" \
  -d '{"experience_years": 5, "education_level": "Master", "skills_match_score": 85}'

2. Match Job:
curl -X POST "http://localhost:8001/api/job-match" \
  -H "Content-Type: application/json" \
  -d '{"resume_score": 0.85, "skills_match_score": 82, "experience_years": 5, "education_level": "Master", "industry": "IT"}'

3. Analyze Skill Gaps:
curl -X POST "http://localhost:8001/api/skill-gap" \
  -H "Content-Type: application/json" \
  -d '{"user_skills": ["Python", "JavaScript"], "target_job": "Data Scientist"}'

4. Predict Salary:
curl -X POST "http://localhost:8001/api/salary-prediction" \
  -H "Content-Type: application/json" \
  -d '{"company_size": "Large", "industry": "IT", "remote_option": true, "num_skills": 5}'

5. Check ML Status:
curl "http://localhost:8001/api/ml-status"


📊 Available Datasets
=====================================================

Resume Screening Dataset (5000+ records):
- Location: datasets/raw/archive1/AI_Resume_Screening_Job_Market_Dataset_2026.csv
- Contains: resume scores, interview results, skills matches, salaries
- Used for: resume quality scoring & job match prediction

Future Jobs Dataset:
- Location: datasets/raw/archive2/future_jobs_dataset.csv
- Contains: job titles, required skills, salaries, locations
- Used for: skill gap analysis & salary prediction


🤖 Trained Models
=====================================================

1. Resume Scorer (resume_scorer.pkl)
   - Input: experience, education, skills_match, industry
   - Output: quality score (0-1), strengths, weaknesses
   - Algorithm: Gradient Boosting

2. Job Matcher (job_matcher.pkl)
   - Input: resume_score, skills, experience, education
   - Output: interview probability (0-1), recommendation
   - Algorithm: Random Forest Classifier

3. Salary Predictor (salary_predictor.pkl)
   - Input: company size, industry, remote, skills count
   - Output: salary range (min, max, avg)
   - Algorithm: Linear Regression

4. Skill Gap Analyzer (skill_gap_analyzer.pkl)
   - Input: user skills, target job
   - Output: missing skills, priority order
   - Algorithm: Rule-based + skill demand ranking


🔌 API Endpoints (5 Total)
=====================================================

POST /api/analyze-resume
POST /api/job-match
POST /api/skill-gap
POST /api/salary-prediction
GET  /api/ml-status


💻 Integration with Flutter App
=====================================================

The Flutter app can now call these endpoints instead of OpenAI!

Example Flutter integration:
```dart
final response = await _client.post(
  Uri.parse('$_baseUrl/api/analyze-resume'),
  headers: {...},
  body: jsonEncode({
    'experience_years': 5,
    'education_level': 'Master',
    'skills_match_score': 85,
  }),
);
```


📁 File Structure
=====================================================

career_lens_backend/
├── app/
│   ├── main.py                          # FastAPI app (now with ML routes)
│   ├── ml_pipeline/                     # ML Training Pipeline
│   │   ├── __init__.py
│   │   ├── data_loader.py               # Load & preprocess datasets
│   │   ├── feature_extractor.py         # Extract ML features
│   │   ├── exploratory_analysis.py      # Data analysis & insights
│   │   ├── model_trainer.py             # Train all 4 models
│   │   └── train_models.py              # Run this to train!
│   ├── services/
│   │   └── ml_service.py                # Load models & make predictions
│   ├── api/
│   │   ├── ml_router.py                 # API endpoints
│   │   └── auth_router.py
│   └── trained_models/                  # Saved trained models
│       ├── resume_scorer.pkl
│       ├── job_matcher.pkl
│       ├── salary_predictor.pkl
│       └── skill_gap_analyzer.pkl
└── datasets/
    └── raw/
        ├── archive1/
        │   └── AI_Resume_Screening_Job_Market_Dataset_2026.csv
        └── archive2/
            └── future_jobs_dataset.csv


🔧 Troubleshooting
=====================================================

Q: "ModuleNotFoundError: No module named 'sklearn'"
A: Run: pip install scikit-learn pandas numpy

Q: "Models not found" error when starting server
A: Run training first: python -m app.ml_pipeline.train_models

Q: "API endpoint not working"
A: Check that ml_router is properly registered in main.py

Q: Want to retrain models with new data?
A: Update the dataset CSV files and re-run: python -m app.ml_pipeline.train_models


✅ Success Indicators
=====================================================

✓ Datasets loaded (5000+ resume records, 100+ job records)
✓ All features extracted correctly
✓ Resume Scorer R² > 0.7
✓ Job Matcher Accuracy > 70%
✓ Salary Predictor RMSE < $20,000
✓ Skill demand rankings updated
✓ Models saved to disk
✓ API endpoints responding with predictions
✓ No OpenAI/Gemini/Groq dependencies needed!
"""
