FROM ghcr.io/home-assistant/aarch64-base-python:3.11-alpine3.18


ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION}

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1

# ------------------------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------------------------
RUN apk add --no-cache \
    bash \
    curl \
    jq \
    tzdata \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    gfortran \
    openblas-dev \
    lapack-dev

# ------------------------------------------------------------------------------
# bashio (HA addon support)
# ------------------------------------------------------------------------------
RUN curl -L -s \
    https://github.com/hassio-addons/bashio/archive/v0.16.2.tar.gz \
    | tar zx -C /tmp \
    && mv /tmp/bashio-* /usr/lib/bashio \
    && ln -s /usr/lib/bashio/bashio /usr/bin/bashio

# ------------------------------------------------------------------------------
# App
# ------------------------------------------------------------------------------
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ /app/src/
COPY dashboard/ /app/dashboard/
COPY notebooks/ /app/notebooks/
COPY config_adapter.py /app/
COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

# ------------------------------------------------------------------------------
# Data dirs
# ------------------------------------------------------------------------------
RUN mkdir -p /data/{models,backups,logs,config}

# ------------------------------------------------------------------------------
# HA Ingress Port
# ------------------------------------------------------------------------------
EXPOSE 3001

CMD ["/app/run.sh"]
