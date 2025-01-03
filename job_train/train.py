import os
import time
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def train_model(dataset_path):
    # Check if the dataset file exists
    if not os.path.isfile(dataset_path):
        print(f"Dataset file '{dataset_path}' not found.")
        return

    # Load the dataset from the CSV file
    data = pd.read_csv(dataset_path)
    print("Dataset:", data)
    print("Dataset loaded successfully.")

    # Separate features and target variable
    if 'target' not in data.columns:
        print("The dataset must contain a 'target' column.")
        return

    X = data.drop('target', axis=1)
    y = data['target']
    print("Data preprocessing completed.")

    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,      # 20% for testing
        random_state=42     # Seed for reproducibility
    )
    print("Data split into training and testing sets.")

    # Initialize and train the Random Forest Classifier
    model = RandomForestClassifier(
        n_estimators=100,   # Number of trees in the forest
        random_state=42     # Seed for reproducibility
    )
    model.fit(X_train, y_train)
    print("Model training completed.")

    # Evaluate the trained model on the test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy on the test set: {accuracy:.2f}")

    # Sleep for demonstration purposes
    time.sleep(10)

    # Save the trained model to the specified directory
    artifacts_dir = '/primeway-artifacts'  # Adjusted directory for user permissions
    os.makedirs(artifacts_dir, exist_ok=True)
    model_path = os.path.join(artifacts_dir, 'model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to '{model_path}'.")


if __name__ == "__main__":
    # Define the path for the dataset file
    dataset_path = '/custom-data/synthetic_dataset.csv'

    # Step 2: Train the model using the dataset from the file
    train_model(dataset_path)
