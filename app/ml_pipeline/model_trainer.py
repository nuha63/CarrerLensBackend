"""
Model Trainer - Train all 4 ML models
"""
import numpy as np
import pickle
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score, classification_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.models_dir = self.project_root / "career_lens_backend/app/trained_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def train_resume_scorer(self, X, y):
        """Train model to predict resume quality score (0-1)"""
        print("\n" + "="*60)
        print("🎓 TRAINING RESUME QUALITY SCORER")
        print("="*60)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Gradient Boosting model
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ Resume Scorer trained!")
        print(f"  MSE: {mse:.4f}")
        print(f"  R² Score: {r2:.4f}")
        print(f"  Sample predictions: {y_pred[:5]}")
        
        self.models['resume_scorer'] = model
        self.scalers['resume_scorer'] = scaler
        self._save_model('resume_scorer', model, scaler)
        
        return model, scaler
    
    def train_job_matcher(self, X, y):
        """Train model to predict interview success (binary classification)"""
        print("\n" + "="*60)
        print("🔗 TRAINING JOB MATCHER")
        print("="*60)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest classifier
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Job Matcher trained!")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Classification Report:")
        print(f"  {classification_report(y_test, y_pred)}")
        
        self.models['job_matcher'] = model
        self.scalers['job_matcher'] = scaler
        self._save_model('job_matcher', model, scaler)
        
        return model, scaler
    
    def train_salary_predictor(self, X, y):
        """Train model to predict salary ranges"""
        print("\n" + "="*60)
        print("💰 TRAINING SALARY PREDICTOR")
        print("="*60)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Linear Regression model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mse)
        
        print(f"✅ Salary Predictor trained!")
        print(f"  RMSE: ${rmse:,.0f}")
        print(f"  R² Score: {r2:.4f}")
        print(f"  Sample predictions: {y_pred[:5].astype(int)}")
        
        self.models['salary_predictor'] = model
        self.scalers['salary_predictor'] = scaler
        self._save_model('salary_predictor', model, scaler)
        
        return model, scaler
    
    def train_skill_gap_analyzer(self, skills_by_job, skill_demand):
        """Train skill gap analyzer (non-ML, rule-based)"""
        print("\n" + "="*60)
        print("📚 TRAINING SKILL GAP ANALYZER")
        print("="*60)
        
        analyzer_data = {
            'skills_by_job': skills_by_job,
            'skill_demand': skill_demand,
            'top_skills': sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:30]
        }
        
        print(f"✅ Skill Gap Analyzer ready!")
        print(f"  Job titles tracked: {len(skills_by_job)}")
        print(f"  Unique skills: {len(skill_demand)}")
        print(f"  Top skill: {analyzer_data['top_skills'][0][0]} (in {analyzer_data['top_skills'][0][1]:.1%} of jobs)")
        
        self.models['skill_gap_analyzer'] = analyzer_data
        self._save_model('skill_gap_analyzer', analyzer_data, None)
        
        return analyzer_data
    
    def _save_model(self, model_name, model, scaler):
        """Save trained model to disk"""
        try:
            model_path = self.models_dir / f"{model_name}.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"  💾 Saved: {model_path}")
            
            if scaler is not None:
                scaler_path = self.models_dir / f"{model_name}_scaler.pkl"
                with open(scaler_path, 'wb') as f:
                    pickle.dump(scaler, f)
                logger.info(f"  💾 Saved: {scaler_path}")
        except Exception as e:
            logger.error(f"❌ Error saving model {model_name}: {e}")
    
    def train_all_models(self, features_dict):
        """Train all 4 models"""
        print("\n" + "🚀 "*30)
        print("STARTING MODEL TRAINING PHASE")
        print("🚀 "*30)
        
        # Train Resume Scorer
        X_resume, y_resume = features_dict['resume']
        self.train_resume_scorer(X_resume, y_resume)
        
        # Train Job Matcher
        X_interview, y_interview = features_dict['interview']
        self.train_job_matcher(X_interview, y_interview)
        
        # Train Salary Predictor
        X_salary, y_salary = features_dict['salary']
        self.train_salary_predictor(X_salary, y_salary)
        
        # Train Skill Gap Analyzer
        skills_by_job = features_dict['skills_by_job']
        skill_demand = features_dict['skill_demand']
        self.train_skill_gap_analyzer(skills_by_job, skill_demand)
        
        print("\n" + "✅ "*30)
        print("ALL MODELS TRAINED SUCCESSFULLY!")
        print("✅ "*30)
        print(f"\n📁 Models saved to: {self.models_dir}")
        
        return self.models


def train_models_from_data(resume_df, jobs_df):
    """Convenience function - train all models from processed data"""
    from .feature_extractor import prepare_all_features
    
    features = prepare_all_features(resume_df, jobs_df)
    trainer = ModelTrainer()
    return trainer.train_all_models(features)
