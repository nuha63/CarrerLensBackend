"""
Data Loader - Load and preprocess datasets for ML training
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self):
        self.resume_data = None
        self.jobs_data = None
        self.merged_data = None
        self.project_root = Path(__file__).parent.parent.parent.parent
        
    def load_datasets(self):
        """Load both datasets from raw folder"""
        try:
            # Load resume screening data
            resume_path = self.project_root / "datasets/raw/archive1/AI_Resume_Screening_Job_Market_Dataset_2026.csv"
            self.resume_data = pd.read_csv(resume_path)
            logger.info(f"✅ Loaded resume data: {self.resume_data.shape[0]} records")
            
            # Load future jobs data
            jobs_path = self.project_root / "datasets/raw/archive2/future_jobs_dataset.csv"
            self.jobs_data = pd.read_csv(jobs_path)
            logger.info(f"✅ Loaded jobs data: {self.jobs_data.shape[0]} records")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error loading datasets: {e}")
            return False
    
    def preprocess_resume_data(self):
        """Clean and prepare resume screening data"""
        df = self.resume_data.copy()
        
        # Handle missing values
        df['skills_match_score'].fillna(df['skills_match_score'].mean(), inplace=True)
        df['resume_score'].fillna(df['resume_score'].mean(), inplace=True)
        df['experience_years'].fillna(df['experience_years'].median(), inplace=True)
        
        # Normalize numeric columns
        df['skills_match_score'] = df['skills_match_score'] / 100.0
        df['resume_score'] = df['resume_score'] / 100.0
        
        # Encode categorical columns
        df['education_encoded'] = pd.factorize(df['education_level'])[0]
        df['location_encoded'] = pd.factorize(df['location_type'])[0]
        df['industry_encoded'] = pd.factorize(df['industry'])[0]
        df['demand_encoded'] = df['job_market_demand'].map({'Low': 0, 'Medium': 1, 'High': 2})
        
        # Binary target for interview_call
        df['interview_call_binary'] = (df['interview_call'] == 'Yes').astype(int)
        
        logger.info("✅ Resume data preprocessing complete")
        return df
    
    def preprocess_jobs_data(self):
        """Clean and prepare jobs data"""
        df = self.jobs_data.copy()
        
        # Extract numeric salary (take midpoint)
        def extract_salary(salary_str):
            try:
                return int(salary_str)
            except:
                return df['salary_usd'].median()
        
        df['salary_numeric'] = df['salary_usd'].apply(extract_salary)
        
        # Encode categorical columns
        df['industry_encoded'] = pd.factorize(df['industry'])[0]
        df['remote_encoded'] = (df['remote_option'] == 'Yes').astype(int)
        df['company_size_encoded'] = df['company_size'].map({'Small': 0, 'Medium': 1, 'Large': 2})
        
        # Extract number of required skills
        df['num_skills'] = df['skills_required'].str.split(',').apply(len)
        
        logger.info("✅ Jobs data preprocessing complete")
        return df
    
    def get_processed_data(self):
        """Get all processed data"""
        if self.resume_data is None or self.jobs_data is None:
            self.load_datasets()
        
        resume_processed = self.preprocess_resume_data()
        jobs_processed = self.preprocess_jobs_data()
        
        return resume_processed, jobs_processed


def load_all_data():
    """Convenience function to load everything"""
    loader = DataLoader()
    loader.load_datasets()
    resume_data, jobs_data = loader.get_processed_data()
    return resume_data, jobs_data
