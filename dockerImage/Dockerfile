## Licensed under the GPL2 License. Refer to the License file.
FROM alpine:latest

WORKDIR /app

COPY ./twamp-protocol-master /app
COPY ./startup.sh /app

RUN apk update
RUN apk upgrade
RUN apk add iperf3 build-base iputils

ENTRYPOINT ["sh", "./startup.sh", "&", "&&", "/bin/sh"]
