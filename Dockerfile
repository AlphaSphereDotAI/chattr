FROM cgr.dev/chainguard/wolfi-base:latest@sha256:4f40641f8e1aaeba87755e96982d9fa9893cfaec6544b11599922f82cf7b0ba8 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:a5727064a0de127bdb7c9d3c1383f3a9ac307d9f2d8a391edc7896c54289ced0 \
     /uv /uvx /usr/bin/

USER nonroot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install chattr

FROM cgr.dev/chainguard/wolfi-base:latest@sha256:4f40641f8e1aaeba87755e96982d9fa9893cfaec6544b11599922f82cf7b0ba8 AS production

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
