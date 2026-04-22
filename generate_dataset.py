import pandas as pd
import numpy as np

np.random.seed(42)

rows = 3000

data = {
    "temperature": np.random.uniform(-5, 40, rows),
    "humidity": np.random.uniform(20, 90, rows),
    "wind_speed": np.random.uniform(0, 15, rows),
    "solar_radiation": np.random.uniform(0, 1000, rows),
    "peak_hour_indicator": np.random.randint(1, 25, rows)
}

df = pd.DataFrame(data)

df["daily_units"] = (
    df["temperature"] * 0.05 +
    df["humidity"] * 0.02 +
    df["wind_speed"] * 0.03 +
    df["solar_radiation"] * 0.001 +
    df["peak_hour_indicator"] * 0.5 +
    np.random.uniform(0.5, 1.5, rows)
)

df["monthly_units"] = df["daily_units"] * 30

df = df.round(2)

df.to_csv("energy_dataset_3000.csv", index=False)

print("✅ Dataset generated successfully!")