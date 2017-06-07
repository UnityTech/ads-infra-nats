FROM registry2.applifier.info:5005/ads-infra-kontrol-alpine-3.5:1.0.0

ENV KONTROL_MODE=master,slave \
    KONTROL_PAYLOAD=/data/state.json \
    KONTROL_CALLBACK="python /home/kontrol/callback.py" \
 	NATS_VERSION=0.9.4

ADD resources/ .
RUN set -ex && \
	apk add --no-cache logrotate && \
    apk add --no-cache --virtual .transient ca-certificates openssl wget && \
    update-ca-certificates && \
	wget https://github.com/nats-io/gnatsd/releases/download/v${NATS_VERSION}/gnatsd-v${NATS_VERSION}-linux-386.zip && \
	unzip gnatsd-v${NATS_VERSION}-linux-386.zip && \
 	mv gnatsd-v${NATS_VERSION}-linux-386/gnatsd /usr/bin/gnatsd && \
 	rm -r gnatsd-v${NATS_VERSION}-linux-386* && \
	apk del .transient
	  