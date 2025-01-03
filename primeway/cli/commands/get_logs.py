import click
import requests

from primeway.constants import BASE_BACKEND_URL


@click.command("getlogs")
@click.argument('job_id')
def get_logs(job_id):
    response = requests.get(f"{BASE_BACKEND_URL}/jobs/{job_id}/logs")
    if response.status_code == 200:
        logs = response.json()  # Assuming the response is a list of logs
        if isinstance(logs, list) and logs:
            print("Job Logs:")
            for log in logs:
                print("log", log)
        elif isinstance(logs, dict) and "logs" in logs:  # Fallback if response is a dict with logs key
            print("Job Logs:")
            for log in logs["logs"]:
                print(log)
        else:
            print("No logs available for this job.")
    else:
        print(f"Failed to retrieve logs: {response.text}")

