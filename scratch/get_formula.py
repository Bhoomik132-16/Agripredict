import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def get_simple_formula():
    try:
        df = pd.read_csv('crop_yield.csv')
        # Features
        X = df[['N', 'P', 'K', 'pH', 'avg_temp_c', 'total_rainfall_mm']]
        y = df['yield']
        
        # Fit a simple linear model
        model = LinearRegression()
        model.fit(X, y)
        
        coeffs = model.coef_
        intercept = model.intercept_
        
        print("Coefficients:")
        features = ['N', 'P', 'K', 'pH', 'temp', 'rain']
        for feat, coef in zip(features, coeffs):
            print(f"{feat}: {coef:.6f}")
        print(f"Intercept: {intercept:.6f}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_simple_formula()
