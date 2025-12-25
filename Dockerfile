FROM cgr.dev/chainguard/wolfi-base:latest@sha256:0d8efc73b806c780206b69d62e1b8cb10e9e2eefa0e4452db81b9fa00b1a5175 AS builder

ARG INSTALL_SOURCE
ARG PYTHON_VERSION

# skipcq: DOK-DL3018
RUN apk add --no-cache build-base git uv

RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install ${INSTALL_SOURCE} --python ${PYTHON_VERSION}

FROM cgr.dev/chainguard/wolfi-base:latest@sha256:0d8efc73b806c780206b69d62e1b8cb10e9e2eefa0e4452db81b9fa00b1a5175 AS production

ENV GRADIO_SERVER_PORT=7860 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    FASTEMBED_CACHE_PATH=/home/nonroot/fastembed \
    PATH=/home/nonroot/.local/bin:$PATH

# skipcq: DOK-DL3018
RUN apk add --no-cache curl libstdc++

WORKDIR /home/nonroot

RUN chown -R nonroot:nonroot /home/nonroot

USER nonroot

COPY --from=builder --chown=nonroot:nonroot --chmod=555 /root/.local/ /home/nonroot/.local/

EXPOSE ${GRADIO_SERVER_PORT}

CMD ["chattr"]
