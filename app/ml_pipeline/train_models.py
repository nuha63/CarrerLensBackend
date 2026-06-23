"""
Train Models Script - Run this to train all ML models
Usage: python -m app.ml_pipeline.train_models
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.ml_pipeline.data_loader import load_all_data
from app.ml_pipeline.exploratory_analysis import run_all_analysis
from app.ml_pipeline.feature_extractor import prepare_all_features
from app.ml_pipeline.model_trainer import ModelTrainer


def main():
    print("\n" + "🚀 "*40)
    print("CAREER LENS - ML MODEL TRAINING PIPELINE")
    print("🚀 "*40 + "\n")
    
    # Step 1: Load datasets
    print("📂 STEP 1: Loading datasets...")
    resume_data, jobs_data = load_all_data()
    
    # Step 2: Exploratory analysis
    print("\n📊 STEP 2: Running exploratory analysis...")
    run_all_analysis(resume_data, jobs_data)
    
    # Step 3: Extract features
    print("\n🔧 STEP 3: Extracting features...")
    features = prepare_all_features(resume_data, jobs_data)
    print("✅ Features extracted successfully!")
    
    # Step 4: Train models
    print("\n🤖 STEP 4: Training models...")
    trainer = ModelTrainer()
    trained_models = trainer.train_all_models(features)
    
    print("\n" + "✅ "*40)
    print("TRAINING COMPLETE!")
    print("✅ "*40)
    print("\n📁 Models saved to: career_lens_backend/app/trained_models/")
    print("🚀 Backend is now ready to use ML predictions!\n")


if __name__ == "__main__":
    main()
