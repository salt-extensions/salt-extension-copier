# The ARG must contain the complete image tag - if it only held the bare
# version, Renovate could not write version updates back to this line and
# would silently skip them (digest-only updates would still work).
ARG PYTHON_TAG=3.14.9-slim-trixie
FROM python:${PYTHON_TAG}@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8

LABEL org.opencontainers.image.source=https://github.com/salt-extensions/salt-extension-copier
LABEL org.opencontainers.image.description="CI container for running prek hooks in Salt extension repos"

# renovate: datasource=pypi depName=prek depType=dev
ARG PREK_VERSION=0.5.7

# renovate: datasource=pypi depName=uv depType=dev
ARG UV_VERSION=0.13.5

# The actionlint hook's shellcheck wrapper uses gh for release provenance
# verification. Debian's gh (2.46) predates `gh attestation` (2.49+), which
# would make the wrapper fail hard (unknown command != its auth-required
# soft-skip), so install a recent release instead.
# renovate: datasource=github-releases depName=gh packageName=cli/cli extractVersion=^v(?<version>.*)$ depType=dev
ARG GH_VERSION=2.103.2

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
    && cd /tmp \
    && gh_archive="gh_${GH_VERSION}_linux_amd64" \
    && python -c "import urllib.request as u; \
        base = 'https://github.com/cli/cli/releases/download/v${GH_VERSION}/'; \
        u.urlretrieve(base + '${gh_archive}.tar.gz', '${gh_archive}.tar.gz'); \
        u.urlretrieve(base + 'gh_${GH_VERSION}_checksums.txt', 'checksums.txt')" \
    && grep " ${gh_archive}.tar.gz\$" checksums.txt | sha256sum -c - \
    && tar -xzf "${gh_archive}.tar.gz" "${gh_archive}/bin/gh" \
    && mv "${gh_archive}/bin/gh" /usr/local/bin/gh \
    && rm -rf "${gh_archive}" "${gh_archive}.tar.gz" checksums.txt \
    && git config --system --add safe.directory '*'
