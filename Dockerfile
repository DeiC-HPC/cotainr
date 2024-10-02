# Stage 1: General ubuntu environment
# FROM ubuntu:latest AS linux-base
FROM ubuntu:latest AS linux-base

ENV LC_CTYPE=C.utf8
ENV UV_PYTHON_INSTALL_DIR="/python"
ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT="/home/cotainr/venv"
ENV UV_PYTHON=python3.12
ENV PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH"

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONBREAKPOINT=ipdb.set_trace

# Update ubuntu
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y tzdata
RUN apt-get install adduser
RUN passwd --delete root
RUN adduser cotainr --disabled-password --gecos ""  #  gecos ==> non-interactive

# Stage 2: Python environment
FROM linux-base AS python-base

RUN apt-get install --no-install-recommends -y build-essential gettext
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./
COPY uv.lock ./
COPY requirements-dev.txt ./
RUN uv sync --frozen --no-dev --no-install-project
RUN uv pip install -r requirements-dev.txt

# Stage 3: Building environment
FROM python-base AS builder-base

WORKDIR /home/cotainr
COPY . /home/cotainr
USER cotainr
