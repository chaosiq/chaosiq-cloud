FROM python:3.8-alpine

LABEL maintainer="ChaosIQ <contact@chaosiq.io>"

RUN apk add --no-cache --virtual build-deps gcc g++ git libffi-dev linux-headers \
        python3-dev musl-dev && \
    pip install --no-cache-dir -q -U pip && \
    pip install --no-cache-dir chaostoolkit && \
    pip install --no-cache-dir chaosiq-cloud && \
    apk del build-deps

ENTRYPOINT ["/usr/local/bin/chaos"]
CMD ["--help"]