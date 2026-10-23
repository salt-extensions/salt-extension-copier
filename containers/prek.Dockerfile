ARG PYTHON_VERSION=3.14.9
FROM python:${PYTHON_VERSION}-slim-trixie@sha256:sha256:b347e2dcbc7f0b6f9fb7182e9da6a187fb10ae715e0692518c1aed0eec94a700

LABEL org.opencontainers.image.source=https://github.com/salt-extensions/salt-extension-copier
LABEL org.opencontainers.image.description="CI container for running prek hooks in Salt extension repos"

# renovate: datasource=pypi depName=prek depType=dev
ARG PREK_VERSION=0.5.7

# renovate: datasource=pypi depName=uv depType=dev
ARG UV_VERSION=0.13.5

# Ensure prek only uses the uv pinned below, never a downloaded one
ENV PREK_UV_SOURCE=none

# The safe.directory config must be on the system level since the
# build-time HOME is not the runtime one (/github/home).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        gcc \
        libc-dev \
        jq \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir --root-user-action=ignore \
        "prek==${PREK_VERSION}" \
        "uv==${UV_VERSION}" \
    && git config --system --add safe.directory '*'
