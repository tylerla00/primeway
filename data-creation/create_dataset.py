import pandas as pd
from sklearn.datasets import make_classification


def create_dataset(dataset_path):
    # Generate a synthetic classification dataset
    X, y = make_classification(
        n_samples=1000,     # Total number of samples
        n_features=20,      # Number of features
        n_informative=15,   # Number of informative features
        n_redundant=5,      # Number of redundant features
        n_classes=2,        # Number of target classes
        random_state=42     # Seed for reproducibility
    )
    print("Synthetic dataset generated.")

    # Create feature names
    feature_names = [f'feature_{i}' for i in range(1, X.shape[1] + 1)]

    # Create a DataFrame from the generated data
    data = pd.DataFrame(X, columns=feature_names)
    data['target'] = y

    # Save the DataFrame to a CSV file
    data.to_csv(dataset_path, index=False)
    print(f"Dataset saved to '{dataset_path}'.")


if __name__ == "__main__":
    # Define the path for the dataset file
    dataset_path = '/synthetic_dataset.csv'

    # Step 1: Create the dataset and save it to a file
    create_dataset(dataset_path)
