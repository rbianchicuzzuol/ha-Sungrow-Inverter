FROM ghcr.io/home-assistant/base:latest
ENV LANG C.UTF-8
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1

# Build arguments
ARG BUILD_VERSION
ARG BUILD_ARCH


WORKDIR /app
COPY requirements.txt ./
RUN apk add --no-cache python3 py3-pip \
    && apk add --no-cache --virtual .build-deps python3-dev build-base \
    && python3 -m venv /opt/venv \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY SunGather/ /app/
COPY run.sh /
COPY config_generator.py /

# Install requirements for add-on
RUN sed -i 's/\r$//' /run.sh && chmod a+x /run.sh

CMD ["/run.sh"]

LABEL \
    io.hass.name="Sungrow Inverter" \
    io.hass.description="Sungrow inverter data via Modbus and MQTT" \
    io.hass.version=${BUILD_VERSION} \
    io.hass.type="addon" \
    io.hass.arch=${BUILD_ARCH}
