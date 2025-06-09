import pandas as pd
import numpy as np
from scipy.fft import fft
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt

# 1️⃣ Load Data
def load_data(path):
    df = pd.read_csv(path, parse_dates=['Timestamp'])
    # Rename columns to match dashboard expectations
    df.rename(columns={
        'Voltage (V)': 'tension',  # Using voltage as tension proxy
        'Vibration (m/s²)': 'vibration',
        'Temperature (°C)': 'remaining_life'  # Using temperature as remaining_life proxy
    }, inplace=True)
    df.set_index('Timestamp', inplace=True)
    return df

# 2️⃣ Preprocessing
def preprocess(df):
    df = df.sort_index().asfreq('1H')
    df.interpolate(method='time', inplace=True)
    df.fillna(method='bfill', inplace=True)
    return df

# 3️⃣ Feature Engineering - UPDATED to match dashboard
def add_features(df):
    # Create the exact features your dashboard expects
    df['tension_mean'] = df['tension'].rolling(window=10, min_periods=1).mean()
    df['tension_std'] = df['tension'].rolling(window=10, min_periods=1).std()
    df['vibration_fft_max'] = np.abs(fft(df['vibration'].values)).max()
    
    # Create target labels based on remaining_life (like in your dashboard)
    bins = [-np.inf, 50, 100, np.inf]
    labels = ['Critical', 'Warning', 'Healthy']
    df['condition'] = pd.cut(df['remaining_life'], bins=bins, labels=labels)
    
    df.dropna(inplace=True)
    return df

# 4️⃣ Model Training - UPDATED for new features
def train_model(df):
    # Use only the features your dashboard expects
    features = [
        'tension_mean',
        'tension_std', 
        'vibration_fft_max'
    ]
    
    X = df[features]
    y = df['condition']  # Use condition instead of fault
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=150, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print("✅ Model trained successfully!")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    # Save model with the correct filename
    joblib.dump(model, 'equipment_fault_predictor.pkl')
    print("✅ Model saved as 'equipment_fault_predictor.pkl'")

# 5️⃣ Prediction - UPDATED for new features
def predict_new(data_point):
    model = joblib.load('equipment_fault_predictor.pkl')
    pred = model.predict(data_point)
    return pred[0]

# 6️⃣ Visualization - UPDATED for tension
def plot_trends(df):
    plt.figure(figsize=(15, 6))
    plt.plot(df.index, df['tension'], label='Tension', alpha=0.7)
    plt.plot(df.index, df['tension_mean'], label='10-period Rolling Mean', linewidth=2)
    plt.title('Tension Trends with Rolling Average')
    plt.ylabel('Tension')
    plt.legend()
    plt.show()

# 🧪 Main Execution
if __name__ == '__main__':
    df = load_data('sensor_maintenance_dataset.csv')
    df = preprocess(df)
    df = add_features(df)
    
    if 'condition' in df.columns:
        train_model(df)
    else:
        print("Error: Target column 'condition' not found in dataset")
    
    # Example prediction using the exact features your dashboard uses
    new_data = pd.DataFrame({
        'tension_mean': [1200.0],
        'tension_std': [20.0],
        'vibration_fft_max': [85.0]
    })
    
    prediction = predict_new(new_data)
    print(f"\nPredicted Condition: {prediction}")
    
    plot_trends(df)
