import click
import requests

from primeway.constants import BASE_BACKEND_URL


@click.command("getjobs")
def get_jobs():
    response = requests.get(f"{BASE_BACKEND_URL}/jobs")
    if response.status_code == 200:
        jobs = response.json()
        if jobs:
            print("Current Jobs:")
            for job in jobs:
                print(f"Job ID: {job['job_id']}, Status: {job['status']}")
        else:
            print("No jobs are currently running.")
    else:
        print(f"Failed to retrieve jobs: {response.text}")
