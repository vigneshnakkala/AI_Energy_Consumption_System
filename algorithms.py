import pandas as pd
from sklearn.linear_model import LinearRegression

# Load dataset
df = pd.read_csv("energy_dataset_modified_1500_rows.csv")

# Features (inputs)
X = df[['temperature', 'humidity', 'wind_speed', 'solar_radiation', 'peak_hour']]

# Target (output)
y = df['energy']

# Train model
model = LinearRegression()
model.fit(X, y)

# Prediction function
def lstm_prediction(features):
    # Use first 5 values only
    input_data = [features[:5]]
    prediction = model.predict(input_data)
    return float(prediction[0])