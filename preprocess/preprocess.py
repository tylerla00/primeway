import os
import time
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

def preprocess_data():
    # Load dataset
    data = load_iris()
    X = data.data
    y = data.target

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Standardize features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    time.sleep(30)
    joblib.dump((X_train, X_test, y_train, y_test), '/primeway-artifacts/preprocessed_data.pkl')
    joblib.dump(scaler, '/primeway-artifacts/scaler.pkl')
    print("Data preprocessed and saved.")

if __name__ == "__main__":
    preprocess_data()