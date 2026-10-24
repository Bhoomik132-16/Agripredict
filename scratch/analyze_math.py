import joblib
import pandas as pd
import numpy as np

def analyze_model():
    try:
        # Load the models
        yield_pipeline = joblib.load('models/yield_prediction_model.pkl')
        crop_pipeline = joblib.load('models/crop_recommendation_model.pkl')
        
        # 1. Extract Scaler Parameters (Yield Model)
        # Pipeline structure: [('preprocessor', ColumnTransformer), ('model', RandomForestRegressor)]
        # preprocessor structure: [('num', Pipeline([imputer, scaler]), numeric_cols), ...]
        preprocessor = yield_pipeline.named_steps['preprocessor']
        num_pipeline = preprocessor.named_transformers_['num']
        scaler = num_pipeline.named_steps['scaler']
        
        numeric_features = ['area', 'N', 'P', 'K', 'pH', 'avg_temp_c', 'total_rainfall_mm']
        
        print("--- SCALER PARAMETERS (Yield Model) ---")
        for i, feat in enumerate(numeric_features):
            mean = scaler.mean_[i]
            scale = scaler.scale_[i]
            print(f"{feat}: mean={mean:.4f}, std={scale:.4f}")
            
        # 2. Extract Feature Importance (Simplified)
        model = yield_pipeline.named_steps['model']
        # Note: Feature importance for OHE features is harder to summarize, 
        # but we can look at the raw importance of the first 7 (numeric)
        importances = model.feature_importances_
        print("\n--- FEATURE IMPORTANCES (First 7 Numeric) ---")
        for i, feat in enumerate(numeric_features):
            print(f"{feat}: {importances[i]:.4f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_model()
