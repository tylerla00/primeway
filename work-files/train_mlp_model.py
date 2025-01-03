import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import os
import boto3
import logging

# Step 1: Define a simple MLP model
class SimpleMLP(nn.Module):
    def __init__(self):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = x.view(-1, 28 * 28)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Step 2: Set up device (GPU if available)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Step 3: Load the dataset
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)

# Step 4: Initialize the model, loss function, and optimizer
model = SimpleMLP().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

# Step 5: Training loop
def train_model(model, train_loader, criterion, optimizer, device, epochs=5):
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
        
        print(f'Epoch [{epoch + 1}/{epochs}], Loss: {running_loss / len(train_loader):.4f}')

# Step 6: Save the model
def save_model(model, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, 'simple_mlp.pth')
    torch.save(model.state_dict(), model_path)
    print(f'Model saved to {model_path}')
    return model_path

# Step 7: Upload model to S3
def upload_to_s3(merged_model_dir: str, bucket_name: str) -> None:
    """
    Upload saved model directory to S3 storage.
    """
    logging.info("connect to s3")
    session = boto3.session.Session()
    s3_client = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id="aws_access_key_id",
        aws_secret_access_key="aws_access_key_id"
    )

    try:
        logging.info("uploading to s3")
        for root, _, files in os.walk(merged_model_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, merged_model_dir)
                s3_object_name = relative_path.replace("\\", "/")  # Ensure that the object key uses '/'

                logging.info(f'Uploading {local_file_path} to {bucket_name}/{s3_object_name}')
                s3_client.upload_file(local_file_path, bucket_name, s3_object_name)
    except Exception as e:
        logging.info(f'Error occurred while uploading to {bucket_name}: {e}')
    else:
        logging.info(f'Successfully uploaded to bucket {bucket_name}')

# Execute the training
train_model(model, train_loader, criterion, optimizer, device)

# Save the trained model
model_dir = './saved_model'
model_path = save_model(model, model_dir)

# Upload the saved model to S3
bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
upload_to_s3(model_dir, bucket_name)
