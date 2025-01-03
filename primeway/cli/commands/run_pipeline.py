import click
import os
import requests

from primeway.constants import BASE_BACKEND_URL


def get_api_token():
    # Retrieve API token from environment variable or config file
    return os.getenv('primeway_API_TOKEN', 'primeway-8diat6yqt9mwWB3mGrrjUA')


@click.command('pipeline')
@click.argument('pipeline_id', required=True)
@click.option('--data-file', type=click.Path(exists=True), default=None, help='Path to the data file to send')
def run_pipeline(pipeline_id, data_file):
    """
    Process the job with the given JOB_ID.

    Arguments:
      JOB_ID  Job ID to start
    """
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    url = f'{BASE_BACKEND_URL}/run-pipeline/{pipeline_id}'

    if data_file:
        with open(data_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers=headers, files=files)
    else:
        response = requests.post(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error occurred while starting job: {response.text}")

# If this script is meant to be executed directly, you can add:
if __name__ == '__main__':
    run_pipeline()