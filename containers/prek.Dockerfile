ARG PYTHON_VERSION=3.14.8
FROM python:${PYTHON_VERSION}-slim-trixie@sha256:fbecd461fc72d21b2143c6eaba25143738079154a6d0ea3da3aec724f50eed4a

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
