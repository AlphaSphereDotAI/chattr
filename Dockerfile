FROM cgr.dev/chainguard/wolfi-base:latest@sha256:c6584af9be8d4aad9b3a41ad3fdc520c3a84e14dd9ae1738b054e8b6df8c5194 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:1e26f9a868360eeb32500a35e05787ffff3402f01a8dc8168ef6aee44aef0aab \
     /uv /uvx /usr/bin/

# skipcq: DOK-DL3018
RUN apk add --no-cache build-base git

USER nonroot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install git+https://github.com/AlphaSphereDotAI/chattr

FROM cgr.dev/chainguard/wolfi-base:latest@sha256:c6584af9be8d4aad9b3a41ad3fdc520c3a84e14dd9ae1738b054e8b6df8c5194 AS production

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
