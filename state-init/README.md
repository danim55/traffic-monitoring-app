# State‑Init Backend Service

This directory contains the backend component responsible for initializing and seeding OpenSearch with required indices and mappings. It's a long‑running Python service managed with [Poetry](https://python-poetry.org/) and packaged as a Docker image for containerized deployment.

---

## Project Structure

```

state-init/           # Root folder
├── state_init/       # Python package
│   └── main.py       # Entry point: connects to OpenSearch and applies indices/mappings
├── tests/            # pytest unit tests
├── pyproject.toml    # Poetry project configuration
├── poetry.lock       # Locked dependency versions
├── Dockerfile        # Builds production container image
└── README.md         # This file

````

---

## Development Workflow

### Prerequisites

- Python 3.12 or higher  
- [Poetry](https://python-poetry.org/docs/#installation)  
- (Optional) `pytest`, `flake8`, `mypy` for testing and linting  

### Setup

```bash
cd state-init            # or your renamed directory
poetry install
poetry shell
````

### Running Locally

```bash
poetry run python -m state_init.main
```

This will connect to your OpenSearch cluster (configured via environment variables) and create the predefined indices and mappings.

### Testing

```bash
poetry run pytest
```

---

## Docker

The `Dockerfile` produces a minimal, production‑ready image:

### Build

```bash
docker build --build-arg ENVIRONMENT=DEV -t ghcr.io/danim55/traffic-monitoring/state-init:0.0.1 .
```

### Run

```bash
docker run --rm \
  -e OPENSEARCH_URL=http://opensearch:9200 \
  -e OPENSEARCH_USER=admin \
  -e OPENSEARCH_PASSWORD=secret \
  state-init:latest
```

Inside the container it runs:

```bash
python -m state_init.main
```

---

## Corporate Proxy Configuration

If you're behind a corporate Artifactory or custom PyPI proxy, the Docker image is preconfigured to:

* Use your internal index URL
* Trust your organization's CA certificates via `REQUESTS_CA_BUNDLE` and `PIP_CERT`

Ensure any internal certs or proxy settings are mounted or baked into the image as needed.
