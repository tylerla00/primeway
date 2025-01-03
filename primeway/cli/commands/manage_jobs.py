import click
import sys
import os
import requests
import shutil
import zipfile
import sseclient
from datetime import datetime

from tabulate import tabulate

from primeway.constants import BASE_BACKEND_URL


def get_api_token():
    # Retrieve API token from environment variable or config file
    token = os.environ.get('primeway_API_TOKEN', 'primeway-8diat6yqt9mwWB3mGrrjUA')
    if not token:
        raise ValueError("The 'primeway_API_TOKEN' is missing from the environment variables.")

    return token


@click.command('list')
@click.option('--status', type=click.Choice(['running', 'completed', 'pending', 'failed']), help='Filter jobs by status.')
@click.option('--pipeline_execution_id', help='Filter jobs by pipeline execution ID.')
def list_jobs(status, pipeline_execution_id):
    """List jobs with optional status and pipeline execution ID filters."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if status:
        params['status'] = status
    if pipeline_execution_id:
        params['pipeline_execution_id'] = pipeline_execution_id
        
    response = requests.get(f'{BASE_BACKEND_URL}/jobs', headers=headers, params=params)
    if response.status_code == 200:
        jobs = response.json()
        if jobs:
            headers_list = ['Job ID', 'Name', 'Type', 'Created', 'Build Status', 'Last Status', 'Last Start', 'Last End', 'Last Status' 'GPU Types']
            table_data = []

            for job in jobs:
                job_id = job['job_id']
                job_name = job['job_name']
                job_type = job['job_type']
                build_status = job['build_status']
                dt = datetime.fromisoformat(job['created_at'].replace('Z', '+00:00'))
                formatted_created_at = dt.strftime('%Y-%m-%d %H:%M:%S')

                exec_status = job.get('status', "Hasn't started")
                start_time = job.get('last_execution_start_time', '')[:19]  if job.get('last_execution_start_time') else ''
                end_time = job.get('last_execution_end_time', '')[:19] if job.get('last_execution_end_time') else ''
                last_status = job.get('last_execution_status', '')[:19] if job.get('last_execution_status') else ''
                gpu_type = job.get('gpu_type') or {}
                gpu_type_str = ', '.join([f"{k}: {v}" for k, v in gpu_type.items()])

                row = [
                    job_id,
                    job_name,
                    job_type,
                    formatted_created_at,
                    build_status,
                    exec_status,
                    start_time,
                    end_time,
                    last_status,
                    gpu_type_str
                ]
                table_data.append(row)

            print(tabulate(table_data, headers=headers_list, tablefmt='grid'))
        else:
            print("No jobs found.")
    else:
        print(f"Error retrieving jobs: {response.text}")


@click.command('executions')
@click.argument('job_id', required=True)
@click.option('--status', help='Filter executions by status.')
def list_executions(job_id, status=None):
    """List all executions for a given job_id, optionally filtered by status."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if status:
        params['status'] = status
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}/executions', headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        job_type = data.get('job_type', '')
        if job_type == "deploy":
            column_type = "Deploy"
        else:
            column_type = "Run"

        executions = data.get('executions', [])
        if executions:
            header_execution_id = f'{column_type} Execution ID' if job_type else 'Execution ID'
            # Collect data into a list of rows
            table_data = []
            for execution in executions:
                execution_id = execution.get('job_execution_id')
                exec_status = execution.get('status')
                dt = datetime.fromisoformat(execution['created'].replace('Z', '+00:00'))
                formatted_created_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                start_time = execution.get('start_time', '')[:19] if execution.get('start_time', '') else ''
                end_time = execution.get('end_time', '')[:19] if execution.get('end_time') else ''
                gpu_type = execution.get('gpu_type', {})
                if job_type == "deploy":
                    health_status = execution.get('health_status')
                    proxy_url = execution.get('proxy_url')
                gpu_types_str = ', '.join([f"{k}: {v}" for k, v in gpu_type.items()])
                if job_type != "deploy":
                    table_data.append([
                        execution_id,
                        exec_status,
                        start_time,
                        end_time,
                        gpu_types_str
                    ])
                    # Prepare headers
                    headers = [header_execution_id, 'Status', 'Created', 'Start Time', 'End Time', 'GPU Types']
                else:
                    table_data.append([
                        execution_id,
                        exec_status,
                        formatted_created_at,
                        health_status,
                        proxy_url,
                        start_time,
                        end_time,
                        gpu_types_str
                    ])
                    # Prepare headers
                    headers = [header_execution_id, 'Status', 'Health', "Url", 'Start Time', 'End Time', 'GPU Types']
            # Print table using tabulate
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
        else:
            print("No executions found for this job.")
    else:
        print(f"Error retrieving executions: {response.text}")


@click.command('info')
@click.option('--job_id', required=True, help='The ID of the job.')
def get_job_info(job_id):
    """Retrieve information about a job."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}', headers=headers)
    if response.status_code == 200:
        job_data = response.json()
        job_type = job_data.get('job_type')

        # Display base job information
        print("\nJob Config:")
        print(f"Job ID          : {job_data.get('job_id')}")
        print(f"Job Type        : {job_type}")
        print(f"Build status    : {job_data.get('build_status')}")
        print(f"Job Name        : {job_data.get('job_name')}")
        print(f"Created At      : {job_data.get('created_at')}")
        print(f"Docker Image    : {job_data.get('docker_image')}")
        print(f"GPU Types       : {job_data.get('gpu_types')}")
        print(f"CPU Count       : {job_data.get('cpu_count')}")
        print(f"Memory          : {job_data.get('memory')}")
        print(f"Disk Space      : {job_data.get('disk_space')}")
        print(f"Environment     : {job_data.get('env')}")
        print(f"Pipeline ID     : {job_data.get('pipeline_id')}")
        print(f"Step Number     : {job_data.get('step_number')}")
        print(f"Dependencies    : {job_data.get('dependencies')}")
        print(f"Inputs          : {job_data.get('inputs')}")
        print(f"Requirements    : {job_data.get('requirements')}")
        print(f"Apt packages    : {job_data.get('apt_packages')}")

        # Display additional fields based on job type
        if job_type == 'deploy':
            print("\nDeploy Job Specific Parameters:")
            print(f"Idle Timeout    : {job_data.get('idle_timeout')}")
            print(f"Schedule Start  : {job_data.get('schedule_start')}")
            print(f"Schedule End    : {job_data.get('schedule_end')}")
            print(f"Health Endpoint : {job_data.get('health_endpoint')}")
            print(f"Port            : {job_data.get('port')}")
        # If there are specific fields for RunJob, handle them here
    else:
        print(f"Error retrieving job information: {response.text}")


@click.command('buildlogs')
@click.argument('job_id', required=True)
def get_buildjob_logs(job_id):
    """Retrieve and display logs for a job or job execution."""
    if not job_id:
        click.echo("Please provide job id")
        sys.exit(1)

    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    # Fetch logs from the API
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}/build-logs', headers=headers)
    if response.status_code == 200:
        logs = response.json().get('build_logs', '')
        click.echo(logs)
    else:
        click.echo(f"Error retrieving logs: {response.text}")
        sys.exit(1)


@click.command('logs')
@click.option('--job-id', help='The ID of the job.')
@click.option('--job-execution-id', help='The ID of the job execution.')
@click.option('--follow', is_flag=True, help='Stream the logs in real time.')
def get_job_logs(job_id, job_execution_id, follow):
    """Retrieve and display logs for a job or job execution."""
    if not job_id and not job_execution_id:
        click.echo("Please provide either --job-id or --job-execution-id.")
        sys.exit(1)

    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    # Prepare query parameters
    params = {'follow': 'true' if follow else 'false'}
    if job_id:
        params['job_id'] = job_id
    elif job_execution_id:
        params['job_execution_id'] = job_execution_id

    # Fetch logs from the API
    response = requests.get(f'{BASE_BACKEND_URL}/job-logs', headers=headers, params=params, stream=True)
    if response.status_code == 200:
        if follow:
            # Stream logs using sseclient
            client = sseclient.SSEClient(response)
            for event in client.events():
                click.echo(event.data)
        else:
            logs = response.json().get('logs', '')
            click.echo(logs)
    else:
        click.echo(f"Error retrieving logs: {response.text}")
        sys.exit(1)


@click.command('artifacts')
@click.option('--job-id', help='The ID of the job.')
@click.option('--job-execution-id', help='The ID of the job execution.')
@click.option('--output-dir', type=click.Path(), help='Directory to save artifacts.')
def get_job_artifacts(job_id, job_execution_id, output_dir):
    """Retrieve artifacts for a job or job execution and save them to a directory."""
    if not job_id and not job_execution_id:
        click.echo("Please provide either --job-id or --job-execution-id.")
        sys.exit(1)

    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    # Prepare query parameters
    params = {}
    if job_id:
        params['job_id'] = job_id
    elif job_execution_id:
        params['job_execution_id'] = job_execution_id

    # Fetch artifacts from the API
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/artifacts', headers=headers, params=params, stream=True)
    if response.status_code == 200:
        # Retrieve the job_execution_id from the Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        filename = ''
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
            job_execution_id_in_filename = filename.replace('artifacts_', '').replace('.zip', '')
        else:
            job_execution_id_in_filename = job_execution_id or 'unknown'

        # Determine the output directory
        if output_dir:
            dir_path = os.path.abspath(output_dir)
        else:
            base_dir_name = f"primeway-artifacts-{job_execution_id_in_filename}"
            dir_path = base_dir_name
            counter = 1
            while os.path.exists(dir_path):
                dir_path = f"{base_dir_name}-{counter}"
                counter += 1
            dir_path = os.path.abspath(dir_path)

        # Create the directory if it doesn't exist
        os.makedirs(dir_path, exist_ok=True)

        # Download and extract the zip file
        zip_file_path = os.path.join(dir_path, f'artifacts.zip')
        with open(zip_file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        # Extract the zip file into the directory
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(dir_path)

        # Remove the zip file after extraction
        os.remove(zip_file_path)

        click.echo(f"Artifacts downloaded and extracted to: {dir_path}")
    else:
        click.echo(f"Error retrieving artifacts: {response.text}")
        sys.exit(1)


@click.command('stop')
@click.argument('job_id')
def stop_job(job_id):
    """Stop a running job."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.post(f'{BASE_BACKEND_URL}/jobs/{job_id}/stop', headers=headers)
    if response.status_code == 200:
        print(f"Job {job_id} stopped successfully.")
    else:
        print(f"Failed to stop job {job_id}: {response.text}")

@click.command('logs')
@click.argument('job_id')
@click.option('--follow', '-f', is_flag=True, help='Follow logs in real time.')
def job_logs(job_id, follow):
    """Retrieve logs for a job."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if follow:
        params['follow'] = '1'
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}/logs', headers=headers, params=params, stream=True)
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
    else:
        print(f"Failed to get logs for job {job_id}: {response.text}")

@click.command('artifacts')
@click.argument('job_id')
@click.option('--output', '-o', type=click.Path(), help='Output directory to save artifacts.')
def job_artifacts(job_id, output):
    """Download artifacts from a job."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(f'{BASE_BACKEND_URL}/jobs/{job_id}/artifacts', headers=headers, stream=True)
    if response.status_code == 200:
        output_dir = output or '.'
        zip_file_path = os.path.join(output_dir, f'{job_id}_artifacts.zip')
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Artifacts downloaded to {zip_file_path}")
    else:
        print(f"Failed to download artifacts for job {job_id}: {response.text}")

# ----------------- Pipelines Commands ----------------- #

def pipelines():
    """Commands related to pipelines."""
    pass

@click.command('list')
@click.option('--status', type=click.Choice(['running', 'completed', 'pending', 'failed']), help='Filter pipelines by status.')
@click.option('--start-date', type=click.DateTime(formats=["%Y-%m-%d"]), help='Filter pipelines created after this date (YYYY-MM-DD).')
@click.option('--end-date', type=click.DateTime(formats=["%Y-%m-%d"]), help='Filter pipelines created before this date (YYYY-MM-DD).')
def list_pipelines(status, start_date, end_date):
    """List pipelines with optional status and date filters."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if status:
        params['status'] = status
    if start_date:
        params['start_date'] = start_date.isoformat()
    if end_date:
        params['end_date'] = end_date.isoformat()
    response = requests.get(f'{BASE_BACKEND_URL}/pipelines', headers=headers, params=params)
    if response.status_code == 200:
        pipelines = response.json()
        if pipelines:
            print(f"{'Pipeline ID':<36} {'Name':<20} {'Status':<10} {'Created At'}")
            for pipeline in pipelines:
                created_at = pipeline['created_at'][:19]
                print(f"{pipeline['pipeline_id']:<36} {pipeline['pipeline_name']:<20} {pipeline['status']:<10} {created_at}")
        else:
            print("No pipelines found.")
    else:
        print(f"Error retrieving pipelines: {response.text}")


@click.command('info')
@click.argument('pipeline_id')
def pipeline_info(pipeline_id):
    """Get detailed info about a pipeline."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(f'{BASE_BACKEND_URL}/pipelines/{pipeline_id}', headers=headers)
    if response.status_code == 200:
        pipeline = response.json()
        print(f"Pipeline ID: {pipeline['pipeline_id']}")
        print(f"Name: {pipeline['pipeline_name']}")
        print(f"User ID: {pipeline['user_id']}")
        print(f"Status: {pipeline['status']}")
        print(f"Created at: {pipeline['created_at']}")
        for execution in pipeline.get('executions', []):
            print(f"  Execution ID: {execution['execution_id']}, Status: {execution['status']}, Start Time: {execution['start_time']}, End Time: {execution['end_time']}")
    else:
        print(f"Error retrieving pipeline info: {response.text}")

@click.command('stop')
@click.argument('pipeline_id')
def stop_pipeline(pipeline_id):
    """Stop a running pipeline."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.post(f'{BASE_BACKEND_URL}/pipelines/{pipeline_id}/stop', headers=headers)
    if response.status_code == 200:
        print(f"Pipeline {pipeline_id} stopped successfully.")
    else:
        print(f"Failed to stop pipeline {pipeline_id}: {response.text}")


# ----------------- Resume Pipelines and Jobs ----------------- #


@click.command('resume')
@click.argument('job_id')
def resume_job(job_id):
    """Resume a stopped job."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.post(f'{BASE_BACKEND_URL}/jobs/{job_id}/resume', headers=headers)
    if response.status_code == 200:
        print(f"Job {job_id} resumed successfully.")
    else:
        print(f"Failed to resume job {job_id}: {response.text}")

@click.command('resume')
@click.argument('pipeline_id')
def resume_pipeline(pipeline_id):
    """Resume a stopped pipeline."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.post(f'{BASE_BACKEND_URL}/pipelines/{pipeline_id}/resume', headers=headers)
    if response.status_code == 200:
        print(f"Pipeline {pipeline_id} resumed successfully.")
    else:
        print(f"Failed to resume pipeline {pipeline_id}: {response.text}")



# ----------------- Statistics for everything ----------------- #


@click.command('stats')
def show_stats():
    """Display summary statistics."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    response = requests.get(f'{BASE_BACKEND_URL}/stats', headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print("Summary Statistics:")
        print(f"Total Jobs: {stats['total_jobs']}")
        print(f"Running Jobs: {stats['running_jobs']}")
        print(f"Completed Jobs: {stats['completed_jobs']}")
        print(f"Failed Jobs: {stats['failed_jobs']}")
        print(f"Success Rate: {stats['success_rate']:.2f}%")
        print()
        print(f"Total Pipelines: {stats['total_pipelines']}")
        print(f"Running Pipelines: {stats['running_pipelines']}")
        print(f"Completed Pipelines: {stats['completed_pipelines']}")
        print(f"Failed Pipelines: {stats['failed_pipelines']}")
        print(f"Pipeline Success Rate: {stats['pipeline_success_rate']:.2f}%")
    else:
        print(f"Failed to retrieve statistics: {response.text}")

