import os
import sys
from database import init_db
from ml_pipeline import train_and_save_models

def main():
    print("--- AgriPredict Project Setup ---")
    
    # 1. Initialize Database
    print("\n[1/3] Initializing Database...")
    if not os.path.exists('agripredict.db'):
        init_db()
    else:
        print("Database already exists. Skipping.")
        
    # 2. Create models directory
    print("\n[2/3] Preparing models directory...")
    os.makedirs('models', exist_ok=True)
    
    # 3. Train ML Models
    print("\n[3/3] Training Machine Learning Models...")
    if not os.path.exists('models/yield_prediction_model.pkl') or '--retrain' in sys.argv:
        train_and_save_models()
    else:
        print("Models already exist. Use --retrain to force retraining.")
        
    print("\nSetup complete! You can now run the project using: python app.py")

if __name__ == "__main__":
    main()
