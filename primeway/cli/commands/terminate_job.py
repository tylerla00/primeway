import click
import requests

from primeway.constants import BASE_BACKEND_URL


@click.command("delete")
@click.argument('job_id')
def terminate_job(job_id):
    response = requests.delete(f"{BASE_BACKEND_URL}/jobs/{job_id}")
    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print(f"Failed to terminate job: {response.text}")
