"""
ML Service - Load trained models and make predictions
"""
import pickle
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLService:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.models_dir = self.project_root / "career_lens_backend/app/trained_models"
        
        self.resume_scorer = None
        self.resume_scorer_scaler = None
        self.job_matcher = None
        self.job_matcher_scaler = None
        self.salary_predictor = None
        self.salary_predictor_scaler = None
        self.skill_gap_analyzer = None
        
        self._load_models()
    
    def _load_models(self):
        """Load all trained models from disk"""
        try:
            # Check if models directory exists
            if not self.models_dir.exists():
                logger.warning(f"⚠️  Models directory not found: {self.models_dir}")
                logger.warning("Please run: python -m app.ml_pipeline.train_models")
                return
            
            # Resume Scorer
            resume_scorer_path = self.models_dir / "resume_scorer.pkl"
            if resume_scorer_path.exists():
                with open(resume_scorer_path, 'rb') as f:
                    self.resume_scorer = pickle.load(f)
                with open(self.models_dir / "resume_scorer_scaler.pkl", 'rb') as f:
                    self.resume_scorer_scaler = pickle.load(f)
                logger.info("✅ Loaded resume_scorer")
            else:
                logger.warning(f"⚠️  resume_scorer.pkl not found")
            
            # Job Matcher
            job_matcher_path = self.models_dir / "job_matcher.pkl"
            if job_matcher_path.exists():
                with open(job_matcher_path, 'rb') as f:
                    self.job_matcher = pickle.load(f)
                with open(self.models_dir / "job_matcher_scaler.pkl", 'rb') as f:
                    self.job_matcher_scaler = pickle.load(f)
                logger.info("✅ Loaded job_matcher")
            else:
                logger.warning(f"⚠️  job_matcher.pkl not found")
            
            # Salary Predictor
            salary_predictor_path = self.models_dir / "salary_predictor.pkl"
            if salary_predictor_path.exists():
                with open(salary_predictor_path, 'rb') as f:
                    self.salary_predictor = pickle.load(f)
                with open(self.models_dir / "salary_predictor_scaler.pkl", 'rb') as f:
                    self.salary_predictor_scaler = pickle.load(f)
                logger.info("✅ Loaded salary_predictor")
            else:
                logger.warning(f"⚠️  salary_predictor.pkl not found")
            
            # Skill Gap Analyzer
            skill_gap_analyzer_path = self.models_dir / "skill_gap_analyzer.pkl"
            if skill_gap_analyzer_path.exists():
                with open(skill_gap_analyzer_path, 'rb') as f:
                    self.skill_gap_analyzer = pickle.load(f)
                logger.info("✅ Loaded skill_gap_analyzer")
            else:
                logger.warning(f"⚠️  skill_gap_analyzer.pkl not found")
            
            models_loaded = sum([
                self.resume_scorer is not None,
                self.job_matcher is not None,
                self.salary_predictor is not None,
                self.skill_gap_analyzer is not None
            ])
            
            if models_loaded == 4:
                logger.info("✅ All models loaded successfully!")
                print("✅ ALL ML MODELS LOADED!")
            else:
                logger.warning(f"⚠️  Only {models_loaded}/4 models loaded")
                print(f"⚠️  Only {models_loaded}/4 models loaded. Run training: python -m app.ml_pipeline.train_models")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def analyze_resume(self, 
                      experience_years: int,
                      education_level: str,
                      skills_match_score: float,
                      location_type: str = "Remote",
                      industry: str = "IT",
                      job_market_demand: str = "High") -> Dict[str, Any]:
        """
        Analyze resume quality
        
        Returns:
            {
                "resume_score": 0-1,
                "match_percentage": 0-100,
                "strengths": [...],
                "weaknesses": [...],
                "suggestions": [...]
            }
        """
        try:
            # Encode categorical variables
            education_map = {'High School': 0, 'Bachelor': 1, 'Master': 2, 'PhD': 3}
            location_map = {'Onsite': 0, 'Hybrid': 1, 'Remote': 2}
            industry_map = {'IT': 0, 'Finance': 1, 'Healthcare': 2, 'E-commerce': 3, 'Other': 4}
            demand_map = {'Low': 0, 'Medium': 1, 'High': 2}
            
            education_encoded = education_map.get(education_level, 1)
            location_encoded = location_map.get(location_type, 2)
            industry_encoded = industry_map.get(industry, 4)
            demand_encoded = demand_map.get(job_market_demand, 2)
            
            # Create feature vector
            features = np.array([[
                experience_years,
                education_encoded,
                skills_match_score / 100.0,
                location_encoded,
                industry_encoded,
                demand_encoded
            ]])
            
            # Scale and predict
            if self.resume_scorer_scaler is None or self.resume_scorer is None:
                raise ValueError("Resume scorer models are not loaded")
                
            features_scaled = self.resume_scorer_scaler.transform(features)
            resume_score = float(self.resume_scorer.predict(features_scaled)[0])
            resume_score = max(0, min(1, resume_score))  # Clamp between 0-1
            
            # Generate insights
            strengths = []
            weaknesses = []
            suggestions = []
            
            if experience_years >= 5:
                strengths.append("Strong experience level")
            else:
                weaknesses.append("Limited experience")
                suggestions.append("Gain more professional experience")
            
            if education_level in ['Master', 'PhD']:
                strengths.append("Advanced education")
            elif education_level == 'High School':
                suggestions.append("Consider pursuing a degree")
            
            if skills_match_score >= 80:
                strengths.append("Excellent skill match")
            else:
                weaknesses.append("Skills could be improved")
                suggestions.append("Develop skills aligned with market demand")
            
            if location_type == 'Remote':
                strengths.append("Flexible work location appeal")
            
            if job_market_demand == 'High':
                strengths.append("Entering high-demand field")
            
            return {
                "resume_score": resume_score,
                "match_percentage": int(resume_score * 100),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "suggestions": suggestions
            }
        except Exception as e:
            logger.error(f"❌ Error analyzing resume: {e}")
            raise
    
    def match_job(self,
                 resume_score: float,
                 skills_match_score: float,
                 experience_years: int,
                 education_level: str,
                 industry: str,
                 job_market_demand: str = "High") -> Dict[str, Any]:
        """
        Predict job match success
        
        Returns:
            {
                "match_score": 0-1,
                "interview_probability": 0-1,
                "recommendation": "Strong/Moderate/Weak"
            }
        """
        try:
            education_map = {'High School': 0, 'Bachelor': 1, 'Master': 2, 'PhD': 3}
            industry_map = {'IT': 0, 'Finance': 1, 'Healthcare': 2, 'E-commerce': 3, 'Other': 4}
            demand_map = {'Low': 0, 'Medium': 1, 'High': 2}
            
            education_encoded = education_map.get(education_level, 1)
            industry_encoded = industry_map.get(industry, 4)
            demand_encoded = demand_map.get(job_market_demand, 2)
            
            # Create feature vector
            features = np.array([[
                resume_score,
                skills_match_score / 100.0,
                experience_years,
                education_encoded,
                industry_encoded,
                demand_encoded
            ]])
            
            # Scale and predict probability
            if self.job_matcher_scaler is None or self.job_matcher is None:
                raise ValueError("Job matcher models are not loaded")
                
            features_scaled = self.job_matcher_scaler.transform(features)
            interview_prob = float(self.job_matcher.predict_proba(features_scaled)[0][1])
            
            # Determine recommendation
            if interview_prob >= 0.75:
                recommendation = "Strong Match"
            elif interview_prob >= 0.5:
                recommendation = "Moderate Match"
            else:
                recommendation = "Weak Match"
            
            return {
                "match_score": interview_prob,
                "interview_probability": interview_prob,
                "recommendation": recommendation,
                "confidence": float(self.job_matcher.predict_proba(features_scaled).max())
            }
        except Exception as e:
            logger.error(f"❌ Error matching job: {e}")
            raise
    
    def predict_salary(self,
                      company_size: str,
                      industry: str,
                      remote_option: bool,
                      num_skills: int) -> Dict[str, Any]:
        """
        Predict salary range
        
        Returns:
            {
                "salary_min": int,
                "salary_max": int,
                "salary_avg": int
            }
        """
        try:
            company_size_map = {'Small': 0, 'Medium': 1, 'Large': 2}
            industry_map = {'IT': 0, 'Finance': 1, 'Healthcare': 2, 'E-commerce': 3, 'Other': 4}
            
            company_encoded = company_size_map.get(company_size, 0)
            industry_encoded = industry_map.get(industry, 4)
            remote_encoded = int(remote_option)
            
            # Create feature vector
            features = np.array([[
                company_encoded,
                industry_encoded,
                remote_encoded,
                num_skills
            ]])
            
            # Scale and predict
            if self.salary_predictor_scaler is None or self.salary_predictor is None:
                raise ValueError("Salary predictor models are not loaded")
                
            features_scaled = self.salary_predictor_scaler.transform(features)
            predicted_salary = float(self.salary_predictor.predict(features_scaled)[0])
            
            # Generate range (convert yearly to monthly)
            monthly_predicted = predicted_salary / 12.0
            salary_min = int(monthly_predicted * 0.85)
            salary_max = int(monthly_predicted * 1.15)
            salary_avg = int(monthly_predicted)
            
            return {
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_avg": salary_avg
            }
        except Exception as e:
            logger.error(f"❌ Error predicting salary: {e}")
            raise
    
    def analyze_skill_gaps(self,
                          user_skills: List[str],
                          target_job: str) -> Dict[str, Any]:
        """
        Analyze skill gaps for target job
        
        Returns:
            {
                "missing_skills": [...],
                "skill_demand": {...},
                "priority_skills": [...]
            }
        """
        try:
            if self.skill_gap_analyzer is None:
                raise ValueError("Skill gap analyzer model is not loaded")
                
            skills_by_job = self.skill_gap_analyzer['skills_by_job']
            skill_demand = self.skill_gap_analyzer['skill_demand']
            
            user_skills_lower = set([s.lower().strip() for s in user_skills])
            target_job_lower = target_job.lower()
            
            # Find matching job in database
            required_skills = set()
            for job_title, skills in skills_by_job.items():
                if target_job_lower in job_title.lower():
                    required_skills.update([s.lower() for s in skills])
            
            # Find missing skills
            missing_skills = list(required_skills - user_skills_lower)
            
            # Rank by demand
            missing_with_demand = [
                (skill, skill_demand.get(skill, 0))
                for skill in missing_skills
            ]
            missing_with_demand.sort(key=lambda x: x[1], reverse=True)
            
            priority_skills = [skill for skill, demand in missing_with_demand[:10]]
            
            return {
                "missing_skills": missing_skills,
                "priority_skills": priority_skills,
                "total_missing": len(missing_skills),
                "skill_demands": dict(missing_with_demand[:10])
            }
        except Exception as e:
            logger.error(f"❌ Error analyzing skill gaps: {e}")
            raise


# Singleton instance
_ml_service_instance = None


def get_ml_service() -> MLService:
    """Get or create ML service singleton"""
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLService()
    return _ml_service_instance
