import json
import os
import sys

import requests

from opensearch.opensearch_service import create_index

INDEX_MAPPINGS_FILE_NAME = "index-mappings.json"


def _get_required_env_var(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        sys.exit(f"Missing required environment variable {var_name}")
    return value


def entry_point() -> None:
    # Opensearch dashboards variable envs
    opensearch_dashboard_host = _get_required_env_var(
        "STATEINIT_OPENSEARCH_DASHBOARDS_HOST"
    )
    opensearch_dashboards_port = _get_required_env_var(
        "STATEINIT_OPENSEARCH_DASHBOARDS_PORT"
    )
    opensearch_dashboard_conf_path = _get_required_env_var(
        "STATEINIT_OPENSEARCH_DASHBOARDS_RESOURCES_PATH"
    )

    load_opensearch_indices(dashboards_conf_file=opensearch_dashboard_conf_path)

    load_opensearch_dashboard_configuration(opensearch_dashboard_conf_path=opensearch_dashboard_conf_path,
                                            opensearch_dashboard_host=opensearch_dashboard_host,
                                            opensearch_dashboard_port=opensearch_dashboards_port)


def load_opensearch_indices(dashboards_conf_file: str) -> None:
    # Load indices from json file
    with open(f"{dashboards_conf_file}/{INDEX_MAPPINGS_FILE_NAME}") as json_file:
        index_mappings = json.load(json_file)

    for index_name, mappings in index_mappings.items():
        create_index(index_name, mappings)


def load_opensearch_dashboard_configuration(opensearch_dashboard_conf_path: str,
                                            opensearch_dashboard_host: str,
                                            opensearch_dashboard_port: str) -> None:
    # OpenSearch Dashboards URL
    opensearch_dashboard_url = f'http://{opensearch_dashboard_host}:{opensearch_dashboard_port}'

    # API endpoint for importing saved objects
    import_endpoint = f'{opensearch_dashboard_url}/api/saved_objects/_import?overwrite=true'

    with open(f"{opensearch_dashboard_conf_path}/export.ndjson", 'rb') as conf_file:

        # Set the file data for the multipart form data
        files = {
            'file': conf_file,
        }

        # Set the headers for the request
        headers = {
            'osd-version': '3.0.0',
        }

        # Send the POST request to import the dashboard
        response = requests.post(import_endpoint, headers=headers, files=files)

    # Check if the request was successful
    if response.status_code == 200:
        print("Dashboard loaded successfully")
    else:
        # Raise an exception to fail the program and trigger pod restart
        raise RuntimeError(
            f"Failed to load the opensearch-dashboard configuration."
            f" Status Code: {response.status_code}, Response: {response.text}")


if __name__ == "__main__":
    entry_point()
