import os
import sys
from typing import Any, Dict, Optional

from opensearchpy import OpenSearch, exceptions


# Singleton client instance
_client: Optional[OpenSearch] = None


def _get_required_env_var(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        sys.exit(f"Missing required environment variable: {var_name}")
    return value


def get_client() -> OpenSearch:
    """
    Return a singleton OpenSearch client configured via environment variables:
      - STATEINIT_OPENSEARCH_HOST
      - STATEINIT_OPENSEARCH_PORT
    """
    global _client
    if _client is None:
        host = _get_required_env_var("STATEINIT_OPENSEARCH_HOST")
        port = int(_get_required_env_var("STATEINIT_OPENSEARCH_PORT"))

        _client = OpenSearch(
            hosts=[{"host": host, "port": port}],
        )
    return _client


def create_index(index_name: str, body: Dict[str, Any]) -> None:
    """
    Create an index with provided settings and mappings.

    :param index_name: Name of the index to create
    :param body: Dictionary containing index settings and mappings
    """
    client = get_client()
    try:
        if client.indices.exists(index=index_name):
            print(f"Index '{index_name}' already exists.")
        else:
            client.indices.create(index=index_name, body=body)
            print(f"Index '{index_name}' created.")
    except exceptions.OpenSearchException as e:
        sys.exit(f"Error creating index '{index_name}': {e}")


def delete_index(index_name: str) -> None:
    """
    Delete the specified index if it exists.
    """
    client = get_client()
    try:
        if client.indices.exists(index=index_name):
            client.indices.delete(index=index_name)
            print(f"Index '{index_name}' deleted.")
        else:
            print(f"Index '{index_name}' does not exist.")
    except exceptions.OpenSearchException as e:
        sys.exit(f"Error deleting index '{index_name}': {e}")
