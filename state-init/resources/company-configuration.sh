#!/usr/bin/env bash
set -euo pipefail

# Default ENV to empty if not provided
ENVIRONMENT="${ENVIRONMENT:-}"

if [ "$ENVIRONMENT" = "DEV" ]; then
    echo "Running company proxy setup for DEV environment…"

    # Ensure OS CA certs are installed
    apt-get update
    apt-get install --no-install-recommends -y ca-certificates
    rm -rf /var/lib/apt/lists/*

    # Use the OS truststore for Python HTTPS
    export REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
    # Tell pip to use the same bundle
    export PIP_CERT="/etc/ssl/certs/ca-certificates.crt"

    # Configure pip to use corporate Artifactory proxy and trust host
    pip config set global.index-url \
        "https://repo.aes.alcatel.fr:8443/artifactory/api/pypi/python-pypipythonorg-remote/simple"

    pip config set global.trusted-host "repo.aes.alcatel.fr"
else
    echo "ENVIRONMENT is not DEV (got '$ENVIRONMENT'), skipping company proxy setup."
fi
