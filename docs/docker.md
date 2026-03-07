# Docker

Use Docker to run and test `notebooklm-py` with login support in an isolated environment.

## Build and run

```bash
# Build the image
docker compose build

# Start a shell in the container (notebooklm CLI available)
docker compose run --rm notebooklm
# Then inside the container:
notebooklm --help
notebooklm status
```

Auth and context are stored in a Docker volume (`notebooklm-data`) so they persist between runs.

### Run tests in the container

To run the full test suite (excluding e2e) inside the container with your repo mounted:

```bash
docker compose run --rm -v "$(pwd):/workspace" notebooklm -c "cd /workspace && pip install -q -e '.[all]' && playwright install chromium 2>/dev/null; pytest -q --ignore=tests/e2e"
```

This installs the package in editable mode with dev deps and runs pytest. Use this to verify the image and package before manual login testing.

## Login (browser auth)

`notebooklm login` opens a browser for Google sign-in. You can do that in two ways:

### Option A: Run the container with X server (recommended)

Use the `notebooklm-x11` service so the browser runs inside the container and displays on your host via X11.

**Linux**

1. Allow X11 connections: `xhost +local:docker`
2. Run the X11-enabled service and log in:
   ```bash
   docker compose run --rm notebooklm-x11
   # Inside the container:
   notebooklm login
   ```

**macOS**

1. Install [XQuartz](https://www.xquartz.org/) and enable “Allow connections from network clients” (XQuartz → Preferences → Security).
2. Restart XQuartz, then in a terminal: `xhost +localhost`
3. Run the X11-enabled service (DISPLAY defaults to `host.docker.internal:0`):
   ```bash
   docker compose run --rm notebooklm-x11
   # Inside the container:
   notebooklm login
   ```

### Option B: Run login on the host, mount auth into the container

1. On your host (with a display), run: `notebooklm login`
2. Use the container with auth mounted:
   ```bash
   docker compose run --rm -v ~/.notebooklm:/root/.notebooklm:ro notebooklm notebooklm list
   ```

## One-off commands

```bash
# Use default volume (persisted auth)
docker compose run --rm notebooklm notebooklm list

# With host auth mounted read-only
docker compose run --rm -v ~/.notebooklm:/root/.notebooklm:ro notebooklm notebooklm list
```

## Image details

- Base: [Playwright Python image](https://playwright.dev/python/docs/docker) (Chromium included).
- Package is installed in the image; no need to mount source unless you are developing.
- `NOTEBOOKLM_HOME` defaults to `/root/.notebooklm` in the container.
