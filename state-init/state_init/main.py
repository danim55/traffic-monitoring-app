import json
import os
import sys

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
    opensearch_dashboard_conf_file = _get_required_env_var(
        "STATEINIT_OPENSEARCH_DASHBOARDS_RESOURCES_PATH"
    )

    load_opensearch_idices(opensearch_dashboard_conf_file)


def load_opensearch_idices(dashboards_conf_file: str) -> None:
    # Load indices from json file
    with open(f"{dashboards_conf_file}/{INDEX_MAPPINGS_FILE_NAME}") as json_file:
        index_mappings = json.load(json_file)

    for index_name, mappings in index_mappings.items():
        create_index(index_name, mappings)


if __name__ == "__main__":
    entry_point()
