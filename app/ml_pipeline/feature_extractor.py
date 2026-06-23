"""
Feature Extractor - Extract features for ML models
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureExtractor:
    def __init__(self):
        self.tfidf_vectorizer = None
        
    def extract_resume_features(self, resume_df):
        """Extract features for resume scoring model"""
        features_dict = {
            'experience_years': resume_df['experience_years'].values,
            'education_encoded': resume_df['education_encoded'].values,
            'skills_match_score': resume_df['skills_match_score'].values,
            'location_encoded': resume_df['location_encoded'].values,
            'industry_encoded': resume_df['industry_encoded'].values,
            'demand_encoded': resume_df['demand_encoded'].values,
        }
        
        X = np.column_stack([
            features_dict['experience_years'],
            features_dict['education_encoded'],
            features_dict['skills_match_score'],
            features_dict['location_encoded'],
            features_dict['industry_encoded'],
            features_dict['demand_encoded'],
        ])
        
        y = resume_df['resume_score'].values
        
        logger.info(f"✅ Extracted resume features: X shape {X.shape}")
        return X, y
    
    def extract_interview_features(self, resume_df):
        """Extract features for job matcher (interview prediction)"""
        X = np.column_stack([
            resume_df['resume_score'].values,
            resume_df['skills_match_score'].values,
            resume_df['experience_years'].values,
            resume_df['education_encoded'].values,
            resume_df['industry_encoded'].values,
            resume_df['demand_encoded'].values,
        ])
        
        y = resume_df['interview_call_binary'].values
        
        logger.info(f"✅ Extracted interview features: X shape {X.shape}")
        return X, y
    
    def extract_salary_features(self, jobs_df):
        """Extract features for salary prediction model"""
        X = np.column_stack([
            jobs_df['company_size_encoded'].values,
            jobs_df['industry_encoded'].values,
            jobs_df['remote_encoded'].values,
            jobs_df['num_skills'].values,
        ])
        
        y = jobs_df['salary_numeric'].values
        
        logger.info(f"✅ Extracted salary features: X shape {X.shape}")
        return X, y
    
    def extract_skills_for_job(self, jobs_df):
        """Extract skills per job title"""
        skills_by_job = {}
        
        for idx, row in jobs_df.iterrows():
            job_title = row['job_title']
            skills = [s.strip() for s in row['skills_required'].split(',')]
            
            if job_title not in skills_by_job:
                skills_by_job[job_title] = set()
            
            skills_by_job[job_title].update(skills)
        
        # Convert sets to lists for serialization
        skills_by_job = {k: list(v) for k, v in skills_by_job.items()}
        
        logger.info(f"✅ Extracted skills: {len(skills_by_job)} unique job titles")
        return skills_by_job
    
    def calculate_skill_demand(self, jobs_df):
        """Calculate skill demand scores"""
        from collections import Counter
        
        all_skills = []
        for skills_str in jobs_df['skills_required']:
            skills = [s.strip() for s in skills_str.split(',')]
            all_skills.extend(skills)
        
        skill_counts = Counter(all_skills)
        total_jobs = len(jobs_df)
        
        # Calculate demand as percentage of jobs requiring the skill
        skill_demand = {
            skill: count / total_jobs 
            for skill, count in skill_counts.items()
        }
        
        # Sort by demand
        skill_demand = dict(sorted(skill_demand.items(), key=lambda x: x[1], reverse=True))
        
        logger.info(f"✅ Calculated skill demand: {len(skill_demand)} unique skills")
        return skill_demand


def prepare_all_features(resume_df, jobs_df):
    """Convenience function to prepare all features"""
    extractor = FeatureExtractor()
    
    # Resume scoring features
    X_resume, y_resume = extractor.extract_resume_features(resume_df)
    
    # Interview prediction features
    X_interview, y_interview = extractor.extract_interview_features(resume_df)
    
    # Salary prediction features
    X_salary, y_salary = extractor.extract_salary_features(jobs_df)
    
    # Skills data
    skills_by_job = extractor.extract_skills_for_job(jobs_df)
    skill_demand = extractor.calculate_skill_demand(jobs_df)
    
    return {
        'resume': (X_resume, y_resume),
        'interview': (X_interview, y_interview),
        'salary': (X_salary, y_salary),
        'skills_by_job': skills_by_job,
        'skill_demand': skill_demand,
    }
