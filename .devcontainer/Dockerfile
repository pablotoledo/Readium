# Use Python base image
ARG VARIANT="3.10"
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        git \
        build-essential \
        wget \
        libimage-exiftool-perl \
        libasound2-dev \
        portaudio19-dev \
        python3-pyaudio \
        swig \
        ffmpeg \
        tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a vscode user if it doesn't exist
RUN if ! id -u vscode >/dev/null 2>&1; then \
        useradd -s /bin/bash -m vscode; \
    fi

# Set working directory
WORKDIR /workspace

# Switch to vscode user
USER vscode

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Verify installations
RUN exiftool -ver && \
    ffmpeg -version