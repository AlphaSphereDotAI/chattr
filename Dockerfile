FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

# Enable bytecode compilation, Copy from the cache instead of linking since it's a mounted volume
ENV DEBIAN_FRONTEND=noninteractive \
    UV_NO_CACHE=true \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy 

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev; 

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev; 

# Place executables in the environment at the front of the path
ENV PATH=/app/.venv/bin:$PATH

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

CMD ["python", "app.py"]