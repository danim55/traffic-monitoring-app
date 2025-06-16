FROM python:3.12-slim

# -----------------COMPANY CONFIGURATION--------------

# # Ensure OS CA certs are installed
# RUN apt-get update && \
#     apt-get install --no-install-recommends -y ca-certificates && \
#     rm -rf /var/lib/apt/lists/*

# # Use the OS truststore for Python HTTPS
# ENV REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
# # Tell pip to use the same bundle
# ENV PIP_CERT="/etc/ssl/certs/ca-certificates.crt"

# # Configure pip to use corporate Artifactory proxy and trust host
# RUN pip config set global.index-url https://repo.aes.alcatel.fr:8443/artifactory/api/pypi/python-pypipythonorg-remote/simple && \
#     pip config set global.trusted-host repo.aes.alcatel.fr

# -----------------END OF COMPANY CONFIGURATION---------

# Install Poetry (pinned version)
RUN pip install poetry==1.4.2

WORKDIR /app

# Copy Poetry config & project metadata
COPY pyproject.toml poetry.lock ./
COPY detector ./detector
RUN touch README.md

# Install only production dependencies
RUN poetry install --without dev

# Default command
ENTRYPOINT ["poetry", "run", "python", "-m", "detector.main"]
