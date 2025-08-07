FROM cgr.dev/chainguard/wolfi-base:latest@sha256:86976a5ad15ee108dc7bd768e06381e0e94245779f5d979659216c987450f040 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:9ac8566d708f42bae522b050004f75ebc7c344bc726d6d4e70f1d308b18c4471 \
     /uv /uvx /usr/bin/

# skipcq: DOK-DL3018
RUN apk add --no-cache build-base git

USER nonroot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install git+https://github.com/AlphaSphereDotAI/chattr

FROM cgr.dev/chainguard/wolfi-base:latest@sha256:86976a5ad15ee108dc7bd768e06381e0e94245779f5d979659216c987450f040 AS production

ENV GRADIO_SERVER_PORT=7860 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    FASTEMBED_CACHE_PATH=/home/nonroot/fastembed \
    PATH=/home/nonroot/.local/bin:$PATH

# skipcq: DOK-DL3018
RUN apk add --no-cache curl libstdc++

USER nonroot

WORKDIR /home/nonroot

COPY --from=builder --chown=nonroot:nonroot --chmod=555 /home/nonroot/.local/ /home/nonroot/.local/

EXPOSE ${GRADIO_SERVER_PORT}

CMD ["chattr"]
