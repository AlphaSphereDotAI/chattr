FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

# Enable bytecode compilation, Copy from the cache instead of linking since it's a mounted volume
ENV DEBIAN_FRONTEND=noninteractive \
    UV_NO_CACHE=true \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy 

# Set to true to enable dev mode
ARG DEV=false

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    if [${DEV} = "true"]; then \
    uv sync --frozen --no-install-project; \
    elif [${DEV} = "false"]; then \
    uv sync --frozen --no-install-project --no-dev; \
    else \
    echo "Invalid value for DEV"; \
    fi

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    if [${DEV} = "true"]; then \
    uv sync --frozen; \
    elif [${DEV} = "false"]; then \
    uv sync --frozen --no-dev; \
    else \
    echo "Invalid value for DEV"; \
    fi

# Place executables in the environment at the front of the path
ENV PATH=/app/.venv/bin:$PATH

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

ARG PORT=8000

EXPOSE $PORT

CMD if [${DEV} = "true"]; then \
    fastapi dev --host 0.0.0.0 --port ${PORT}; \
    elif [${DEV} = "false"]; then \
    fastapi run --host 0.0.0.0 --port ${PORT}; \
    else \
    echo "Invalid value for DEV"; \
    fi