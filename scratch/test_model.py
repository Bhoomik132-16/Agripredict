import joblib
import pandas as pd

try:
    crop_model = joblib.load('models/crop_recommendation_model.pkl')
    print("Model loaded.")
except Exception as e:
    print(f"Error: {e}")
    exit()

states = ["Punjab", "Kerala", "Assam"]
test_data = []

for state in states:
    # Typical values for some other crop (e.g., Wheat in Punjab)
    test_data.append({
        'state': state,
        'N': 150, 'P': 50, 'K': 40, 'pH': 8.0, 
        'avg_temp_c': 20, 'total_rainfall_mm': 500
    })
    # Typical values for Rice
    test_data.append({
        'state': state,
        'N': 80, 'P': 40, 'K': 40, 'pH': 6.5, 
        'avg_temp_c': 28, 'total_rainfall_mm': 2000
    })

df = pd.DataFrame(test_data)
predictions = crop_model.predict(df)

for i, pred in enumerate(predictions):
    print(f"Input {i} (State: {test_data[i]['state']}): Predicted Crop -> {pred}")
