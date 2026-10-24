import joblib
import pandas as pd
import numpy as np

try:
    yield_model = joblib.load('models/yield_prediction_model.pkl')
    crop_model = joblib.load('models/crop_recommendation_model.pkl')
    print("Models loaded.")

    # Test data
    test_data = pd.DataFrame([{
        'state': 'Maharashtra',
        'crop': 'Rice',
        'season': 'Kharif',
        'area': 5.0,
        'N': 50.0,
        'P': 25.0,
        'K': 30.0,
        'pH': 6.5,
        'avg_temp_c': 28.0,
        'total_rainfall_mm': 1000.0
    }])

    yield_pred = yield_model.predict(test_data)[0]
    print(f"Predicted Yield: {yield_pred}")

    input_data_crop = test_data[['state', 'N', 'P', 'K', 'pH', 'avg_temp_c', 'total_rainfall_mm']]
    crop_pred = crop_model.predict(input_data_crop)[0]
    print(f"Recommended Crop: {crop_pred}")

except Exception as e:
    print(f"Error: {e}")
