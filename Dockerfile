FROM python:3.13@sha256:5f69d22a88dd4cc4ee1576def19aef48c8faa1b566054c44291183831cbad13b AS builder

SHELL ["/bin/bash", "-c"]

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:2fd1b38e3398a256d6af3f71f0e2ba6a517b249998726a64d8cfbe55ab34af5e \
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

FROM python:3.13-slim@sha256:f2fdaec50160418e0c2867ba3e254755edd067171725886d5d303fd7057bbf81 AS production

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
