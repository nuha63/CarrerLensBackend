"""
Exploratory Data Analysis - Understand datasets before training
"""
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_resume_data(df):
    """Analyze resume screening dataset"""
    print("\n" + "="*60)
    print("📊 RESUME DATA ANALYSIS")
    print("="*60)
    
    print(f"\nDataset Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\n📈 Numeric Statistics:")
    print(f"  Experience years - Mean: {df['experience_years'].mean():.1f}, Range: {df['experience_years'].min()}-{df['experience_years'].max()}")
    print(f"  Resume score - Mean: {df['resume_score'].mean():.1f}, Std: {df['resume_score'].std():.1f}")
    print(f"  Skills match - Mean: {df['skills_match_score'].mean():.1f}, Std: {df['skills_match_score'].std():.1f}")
    
    print("\n🏢 Categorical Distribution:")
    print(f"  Job titles ({df['job_title'].nunique()} unique):")
    print(df['job_title'].value_counts().head(10))
    
    print(f"\n  Industries ({df['industry'].nunique()} unique):")
    print(df['industry'].value_counts())
    
    print(f"\n  Education levels:")
    print(df['education_level'].value_counts())
    
    print(f"\n  Location types:")
    print(df['location_type'].value_counts())
    
    print(f"\n  Job market demand:")
    print(df['job_market_demand'].value_counts())
    
    print("\n🎯 Target Variables:")
    print(f"  Interview calls - Yes: {(df['interview_call']=='Yes').sum()} ({(df['interview_call']=='Yes').sum()/len(df)*100:.1f}%)")
    print(f"  AI screening - Selected: {(df['ai_screening_result']=='Selected').sum()} ({(df['ai_screening_result']=='Selected').sum()/len(df)*100:.1f}%)")
    
    print("\n✅ Resume data analysis complete!")


def analyze_jobs_data(df):
    """Analyze future jobs dataset"""
    print("\n" + "="*60)
    print("🔮 FUTURE JOBS DATA ANALYSIS")
    print("="*60)
    
    print(f"\nDataset Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\n📊 Salary Statistics:")
    print(f"  Mean salary: ${df['salary_usd'].mean():,.0f}")
    print(f"  Median salary: ${df['salary_usd'].median():,.0f}")
    print(f"  Range: ${df['salary_usd'].min():,.0f} - ${df['salary_usd'].max():,.0f}")
    
    print("\n🏢 Job Categories:")
    print(f"  Job titles ({df['job_title'].nunique()} unique):")
    print(df['job_title'].value_counts().head(10))
    
    print(f"\n  Industries ({df['industry'].nunique()} unique):")
    print(df['industry'].value_counts())
    
    print(f"\n  Locations ({df['location'].nunique()} unique):")
    print(df['location'].value_counts().head(10))
    
    print(f"\n  Company sizes:")
    print(df['company_size'].value_counts())
    
    print(f"\n  Remote options:")
    print(df['remote_option'].value_counts())
    
    print("\n💼 Skills Analysis:")
    all_skills = []
    for skills_str in df['skills_required']:
        skills = [s.strip() for s in skills_str.split(',')]
        all_skills.extend(skills)
    
    from collections import Counter
    top_skills = Counter(all_skills).most_common(15)
    print(f"  Top 15 in-demand skills:")
    for skill, count in top_skills:
        print(f"    - {skill}: {count} positions ({count/len(df)*100:.1f}%)")
    
    print("\n✅ Jobs data analysis complete!")


def correlations(resume_df):
    """Analyze correlations in resume data"""
    print("\n" + "="*60)
    print("📈 CORRELATION ANALYSIS")
    print("="*60)
    
    numeric_cols = ['experience_years', 'skills_match_score', 'resume_score']
    correlations_with_interview = {}
    
    for col in numeric_cols:
        corr = resume_df[col].corr(resume_df['resume_score'])
        correlations_with_interview[col] = corr
        print(f"  {col} → resume_score: {corr:.3f}")
    
    print("\n✅ Correlation analysis complete!")


def run_all_analysis(resume_df, jobs_df):
    """Run complete exploratory analysis"""
    print("\n" + "🚀 "*20)
    print("STARTING EXPLORATORY DATA ANALYSIS")
    print("🚀 "*20)
    
    analyze_resume_data(resume_df)
    analyze_jobs_data(jobs_df)
    correlations(resume_df)
    
    print("\n" + "✅ "*20)
    print("ANALYSIS COMPLETE - Ready for model training!")
    print("✅ "*20 + "\n")
