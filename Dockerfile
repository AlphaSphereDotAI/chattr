FROM python:3.13@sha256:4ea77121eab13d9e71f2783d7505f5655b25bb7b2c263e8020aae3b555dbc0b2 AS builder

SHELL ["/bin/bash", "-c"]

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:ef11ed817e6a5385c02cd49fdcc99c23d02426088252a8eace6b6e6a2a511f36 \
    /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --no-install-project --no-dev --locked --no-editable

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --locked --no-editable

FROM python:3.13-slim@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419 AS production

SHELL ["/bin/bash", "-c"]

ENV GRADIO_SERVER_PORT=7860 \
    GRADIO_SERVER_NAME=0.0.0.0

RUN groupadd app && \
    useradd -m -g app -s /bin/bash app && \
    apt-get update > /dev/null && \
    apt-get install -y --no-install-recommends curl > /dev/null && \
    apt-get clean > /dev/null && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

COPY --from=builder --chown=app:app --chmod=555 /app/.venv /app/.venv

USER app

EXPOSE ${GRADIO_SERVER_PORT}

CMD ["/app/.venv/bin/chattr"]
