FROM cgr.dev/chainguard/wolfi-base:latest@sha256:c15643c480330cc703bc100378c97b51dbc7c6480ab335b926945f2d24ed878b AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:f3660c56d5b08d6c516360981bedc439f499b9bf37f46a216018da3777a74011 \
     /uv /uvx /usr/bin/

USER nonroot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install chattr

FROM cgr.dev/chainguard/wolfi-base:latest@sha256:c15643c480330cc703bc100378c97b51dbc7c6480ab335b926945f2d24ed878b AS production

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
