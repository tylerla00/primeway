import click
import os
import tempfile
import shutil
import requests
import yaml

from primeway.constants import BASE_BACKEND_URL


@click.command("pipeline")
@click.option('--config', '-c', type=click.Path(exists=True), required=True, help="Path to the YAML configuration file.")
def create_pipeline(config):
    # Load the configuration data from the YAML file
    with open(config, 'r') as file:
        pipeline_data = yaml.safe_load(file)

    if 'primeway_api_token' not in pipeline_data:
        # Try to get the token from the environment variable
        api_token = os.environ.get('primeway_API_TOKEN')
        if api_token:
            pipeline_data['primeway_api_token'] = api_token
        else:
            raise ValueError("The 'primeway_api_token' is missing from both the configuration file and the environment variables.")
    else:
        api_token = pipeline_data.get('primeway_api_token')

    pipeline_dir = "pipeline_dir"

    with tempfile.TemporaryDirectory() as temp_dir:
        pipeline_base_dir = os.path.join(temp_dir, pipeline_dir)
        os.makedirs(pipeline_base_dir)

        # Copy the pipeline config file into the pipeline base directory
        config_basename = os.path.basename(config)
        shutil.copy2(config, os.path.join(pipeline_base_dir, config_basename))

        # Create subdirectories for each step
        for step in pipeline_data.get('steps', []):
            # Get 'project_dir' and 'entry_script' if they exist
            project_dir = step.get('project_dir')
            entry_script = step.get('entry_script')

            if project_dir is not None:
                project_dir = os.path.abspath(project_dir)
                project_base_name = os.path.basename(os.path.normpath(project_dir))
                step_dir = os.path.join(pipeline_base_dir, project_base_name)
                os.makedirs(step_dir, exist_ok=True)

                # Prepare exclude patterns
                ignore_patterns = step.get('ignore_patterns', [])
                exclude_files = []
                if entry_script:
                    exclude_files.append(entry_script)

                # Copy the files to the step directory, excluding specified patterns
                for item in os.listdir(project_dir):
                    if item not in exclude_files:
                        s = os.path.join(project_dir, item)
                        d = os.path.join(step_dir, item)
                        if os.path.isdir(s):
                            shutil.copytree(s, d, ignore=shutil.ignore_patterns(*ignore_patterns))
                        else:
                            if not any(shutil.fnmatch.fnmatch(item, pattern) for pattern in ignore_patterns):
                                shutil.copy2(s, d)

                # Copy entry script separately if needed
                if entry_script:
                    shutil.copy2(os.path.join(project_dir, entry_script), step_dir)

        # Create a zip of the entire pipeline directory
        zip_base_name = os.path.join(temp_dir, 'pipeline')
        shutil.make_archive(zip_base_name, 'zip', pipeline_base_dir)
        zip_file_path = zip_base_name + '.zip'

        # Now send both the config file and the pipeline zip file to the backend
        with open(config, 'rb') as config_file, open(zip_file_path, 'rb') as pipeline_zip_file:
            files = {
                'config_file': ('config.yaml', config_file, 'application/x-yaml'),
                'pipeline_file': ('pipeline.zip', pipeline_zip_file, 'application/zip')
            }
            headers = {
                'Authorization': f'Bearer {api_token}'
            }

            # Submit the pipeline to the backend
            backend_url = f"{BASE_BACKEND_URL}/create-pipeline"
            with requests.post(backend_url, headers=headers, files=files, stream=True) as response:
                if response.status_code == 200:
                    print("Pipeline submitted successfully")
                    # Stream logs as they arrive
                    for line in response.iter_lines():
                        if line:
                            print(line.decode('utf-8'))
                else:
                    print(f"Failed to submit pipeline: {response.text}")

# if __name__ == '__main__':
#     submit_pipeline()