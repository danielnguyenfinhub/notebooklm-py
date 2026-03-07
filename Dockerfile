# notebooklm-py test container with browser support for login
# Uses official Playwright image so Chromium is pre-installed.
# See docs/docker.md for login and usage.

# Pin to Playwright image that includes Chromium and system deps (see https://playwright.dev/python/docs/docker)
ARG PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright/python:v1.58.0-jammy
FROM ${PLAYWRIGHT_IMAGE}

WORKDIR /app

# Install the package in editable mode with browser support (playwright already in base image)
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

# Hatchling build; no need to copy full repo for install
RUN pip install --no-cache-dir -e ".[browser]"

# Persist notebooklm data (auth, context) at /root/.notebooklm by default
ENV NOTEBOOKLM_HOME=/root/.notebooklm
VOLUME ["/root/.notebooklm"]

WORKDIR /workspace
ENTRYPOINT ["notebooklm"]
CMD ["--help"]
