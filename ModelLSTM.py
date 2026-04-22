import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# Generate sample dataset (replace this with your actual dataset)
np.random.seed(42)
data = np.random.rand(1000, 9)  # Assuming 9 features
labels = np.random.rand(1000, 1)  # Output

# Normalize data
scaler = MinMaxScaler()
data = scaler.fit_transform(data)

# Reshape data for LSTM (samples, timesteps, features)
X_train = data.reshape((data.shape[0], 1, data.shape[1]))
y_train = labels

# Build LSTM model
model = Sequential([
    LSTM(50, activation='relu', input_shape=(1, 9)),
    Dense(1, activation='linear')
])

model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X_train, y_train, epochs=10, batch_size=16)

# Save the trained model
model.save("lstm_model.h5")

print("✅ LSTM Model saved as lstm_model.h5")
