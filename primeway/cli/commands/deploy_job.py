import click
import os
import tempfile
import shutil
import requests
import yaml

from primeway.constants import BASE_BACKEND_URL


@click.command("deploy")
@click.argument('script', required=False, type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), required=True, help="Path to the YAML configuration file.")
def deploy(script, config):
    with open(config, 'r') as file:
        config_data = yaml.safe_load(file)

    headers = {
        'Authorization': f'Bearer {config_data["primeway_api_token"]}'
    }

    backend_url = f"{BASE_BACKEND_URL}/deploy-model"

    if script:
        ignore_patterns = config_data.get('ignore_patterns', [])
        script_path = os.path.abspath(script)
        script_dir = os.path.dirname(script_path)
        entry_script_basename = os.path.basename(script_path)
        config_basename = os.path.basename(config)
        config_data["entry_script_path"] = entry_script_basename

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = os.path.join(temp_dir, 'project.zip')
            config_file_path = os.path.join(temp_dir, 'config.yaml')

            # Write the modified config_data to this file
            with open(config_file_path, 'w') as f:
                yaml.safe_dump(config_data, f)

            modified_script_path = os.path.join(temp_dir, entry_script_basename)
            with open(script_path, 'r') as original_file:
                original_content = original_file.read()

            stripped_content = remove_decorator(original_content)
            with open(modified_script_path, 'w') as modified_file:
                modified_file.write(stripped_content)

            exclude_files = [entry_script_basename, config_basename]

            # Copy other files from script_dir to temp_dir
            for item in os.listdir(script_dir):
                if item in exclude_files:
                    continue  # Skip the main script and config file
                s = os.path.join(script_dir, item)
                d = os.path.join(temp_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, ignore=shutil.ignore_patterns(*ignore_patterns))
                else:
                    shutil.copy2(s, d)

            # Zip the directory, excluding ignored files
            zip_directory(temp_dir, zip_file_path, ignore_patterns)

            with open(config_file_path, 'rb') as config_file, open(zip_file_path, 'rb') as project_file:
                files = {
                    'config_file': ('config.yaml', config_file, 'application/x-yaml'),
                    'project_file': ('project.zip', project_file, 'application/zip')
                }

                # Submit the deployment to the backend
                with requests.post(backend_url, headers=headers, files=files) as response:
                    if response.status_code == 200:
                        print(response.json())
                    else:
                        print(f"Failed to submit deployment: {response.text}")
    else:
        # No script provided, send only the config file
        with open(config, 'rb') as config_file:
            files = {
                'config_file': ('config.yaml', config_file, 'application/x-yaml'),
            }

            # Submit the deployment to the backend
            with requests.post(backend_url, headers=headers, files=files) as response:
                if response.status_code == 200:
                    print(response.json())
                else:
                    print(f"Failed to submit deployment: {response.text}")

if __name__ == '__main__':
    deploy()
