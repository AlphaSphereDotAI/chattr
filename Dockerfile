FROM cgr.dev/chainguard/wolfi-base:latest@sha256:d7032b02de971d3ef61b8e90bbd7c9e16e7889db9391f38ceb5482089dd35c2e AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:f64ad69940b634e75d2e4d799eb5238066c5eeda49f76e782d4873c3d014ea33 \
     /uv /uvx /usr/bin/

USER nonroot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install chattr

FROM cgr.dev/chainguard/wolfi-base:latest@sha256:d7032b02de971d3ef61b8e90bbd7c9e16e7889db9391f38ceb5482089dd35c2e AS production

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
