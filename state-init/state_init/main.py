import os
import sys


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


if __name__ == "__main__":
    entry_point()
