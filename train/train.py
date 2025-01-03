import os
import time
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_model():
    # Load preprocessed data
    X_train, X_test, y_train, y_test = joblib.load(f'{os.getenv("ARTIFACT_DIR_FROM_STEP_1")}/preprocessed_data.pkl')

    # Initialize and train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")
    time.sleep(30)

    # Save trained model
    joblib.dump(model, '/training_artifacts/model.pkl')
    print("Model trained and saved.")

if __name__ == "__main__":
    train_model()