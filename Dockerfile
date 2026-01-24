FROM cgr.dev/chainguard/wolfi-base:latest@sha256:9d9881ff9de0b66fb58bc98f5531c710f1b24d84c18d5751700e11b68c5e2d6c AS builder

ARG INSTALL_SOURCE
ARG PYTHON_VERSION

# skipcq: DOK-DL3018
RUN apk add --no-cache build-base git uv

USER nonroot

RUN --mount=type=cache,target=/root/.cache/uv \
    uv tool install ${INSTALL_SOURCE} --python ${PYTHON_VERSION}

FROM cgr.dev/chainguard/wolfi-base:latest@sha256:9d9881ff9de0b66fb58bc98f5531c710f1b24d84c18d5751700e11b68c5e2d6c AS production

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
