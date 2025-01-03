import os
import sys
import click
import requests
import json

from tabulate import tabulate

from primeway.constants import BASE_BACKEND_URL


def get_api_token():
    # Retrieve API token from environment variable or config file
    return os.getenv('primeway_API_TOKEN', 'primeway-8diat6yqt9mwWB3mGrrjUA')


@click.command('list')
@click.option('--status', type=click.Choice(['running', 'completed', 'pending', 'failed']), help='Filter pipelines by status.')
def list_pipelines(status):
    """List pipelines with optional status filter."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if status:
        params['status'] = status

    response = requests.get(f'{BASE_BACKEND_URL}/pipelines', headers=headers, params=params)
    if response.status_code == 200:
        pipelines = response.json()
        if pipelines:
            headers_list = ['Pipeline ID', 'Name', 'Build Status', 'Created At', 'Last Execution Status', 'Start Time', 'End Time']
            table_data = []

            for pipeline in pipelines:
                pipeline_id = pipeline['pipeline_id']
                pipeline_name = pipeline['pipeline_name']
                build_status = pipeline['build_status']
                created_at = pipeline['created_at']

                last_execution = pipeline.get('last_execution') or {}
                exec_status = last_execution.get('status', 'No execution')
                start_time = (last_execution.get('start_time') or '')[:19]
                end_time = (last_execution.get('end_time') or '')[:19]

                row = [
                    pipeline_id,
                    pipeline_name,
                    build_status,
                    created_at,
                    exec_status,
                    start_time,
                    end_time
                ]
                table_data.append(row)

            print(tabulate(table_data, headers=headers_list, tablefmt='grid'))
        else:
            print("No pipelines found.")
    else:
        print(f"Error retrieving pipelines: {response.text}")


@click.command('buildlogs')
@click.argument('pipeline_id', required=True)
def get_pipeline_buildlogs(pipeline_id):
    """Retrieve and display build logs for pipeline."""
    if not pipeline_id:
        click.echo("Please provide pipeline id")
        sys.exit(1)

    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}

    # Fetch logs from the API
    response = requests.get(f'{BASE_BACKEND_URL}/pipelines/{pipeline_id}/build-logs', headers=headers)
    if response.status_code == 200:
        logs = response.json().get('build_logs', '')
        click.echo(logs)
    else:
        click.echo(f"Error retrieving logs: {response.text}")
        sys.exit(1)


@click.command('executions')
@click.option('--pipeline_id', required=True, help='The ID of the pipeline.')
@click.option('--status', help='Filter executions by status.')
def list_pipeline_executions(pipeline_id, status=None):
    """List all executions for a given pipeline_id, optionally filtered by status."""
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    params = {}
    if status:
        params['status'] = status

    # Make the API request to get pipeline executions
    response = requests.get(
        f'{BASE_BACKEND_URL}/pipelines/{pipeline_id}/executions',
        headers=headers,
        params=params
    )

    if response.status_code == 200:
        executions = response.json()
        if executions:
            # Prepare data for tabulate
            table_data = []
            for execution in executions:
                execution_id = execution.get('execution_id')
                exec_status = execution.get('status')
                start_time = execution.get('start_time', '')[:19] if execution.get('start_time') else ''
                end_time = execution.get('end_time', '')[:19] if execution.get('end_time') else ''
                table_data.append([execution_id, exec_status, start_time, end_time])

            # Define table headers
            headers = ['Execution ID', 'Status', 'Start Time', 'End Time']

            # Print the table
            print(tabulate(table_data, headers=headers, tablefmt='grid'))
        else:
            print("No executions found for this pipeline.")
    else:
        print(f"Error retrieving executions: {response.text}")


@click.command('details')
@click.option('--pipeline_id', required=True, help='The ID of the pipeline.')
@click.option('--execution_id', required=True, help='The ID of the pipeline execution.')
def get_pipeline_execution_details(pipeline_id, execution_id):
    """
    Retrieve and display detailed information about a specific pipeline execution.
    """
    api_token = get_api_token()
    headers = {'Authorization': f'Bearer {api_token}'}
    # Make the API request to get pipeline executions
    response = requests.get(
        f'{BASE_BACKEND_URL}/pipelines/{pipeline_id}/executions/{execution_id}',
        headers=headers,
    )

    if response.status_code == 200:
        execution_details = response.json()

        # Display execution details
        click.echo(f"\nPipeline Execution Details:")
        click.echo(f"Execution ID: {execution_details.get('execution_id')}")
        click.echo(f"Pipeline ID: {execution_details.get('pipeline_id')}")
        click.echo(f"Status: {execution_details.get('status')}")
        click.echo(f"Start Time: {execution_details.get('start_time', '')[:19]}")
        click.echo(f"End Time: {execution_details.get('end_time', '')[:19]}")
        click.echo()

        # Display steps in a table format
        steps = execution_details.get('steps', {})

        if not steps:
            click.echo("No steps available for this execution.")
            return
        
        sorted_steps = sorted(
            steps.items(),
            key=lambda item: int(item[1].get('step_number', float('inf'))) if item[1].get('step_number') != 'N/A' else float('inf')
        )

        table_headers = [
            'Step ID',
            'Job ID',
            'Job Name',
            'Status',
            'Start Time',
            'End Time',
            'Dependencies',
            'Inputs',
            'Step Number'
        ]

        table_rows = []

        for step_id, step_info in sorted_steps:
            job_id = step_info.get('job_id', 'N/A')
            job_name = step_info.get('job_name', 'N/A')
            status = step_info.get('status', 'N/A')
            dependencies = ', '.join(step_info.get('dependencies', [])) if step_info.get('dependencies') else 'None'
            inputs = json.dumps(step_info.get('inputs', {}), indent=2) if step_info.get('inputs') else 'None'
            step_number = step_info.get('step_number', 'N/A')
            start_time = step_info.get('start_time', 'N/A')
            end_time = step_info.get('end_time', 'N/A')

            if start_time and start_time != 'N/A':
                start_time = str(start_time)[:19]
            else:
                start_time = 'N/A'
            if end_time and end_time != 'N/A':
                end_time = str(end_time)[:19]
            else:
                end_time = 'N/A'

            table_rows.append([
                step_id,
                job_id,
                job_name,
                status,
                start_time,
                end_time,
                dependencies,
                inputs,
                step_number
            ])

        click.echo(tabulate(table_rows, headers=table_headers, tablefmt='pretty'))
    else:
        print(f"Error retrieving job information: {response.text}")
