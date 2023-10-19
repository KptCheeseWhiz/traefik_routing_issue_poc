FROM alpine:3.18.2
WORKDIR /app

RUN apk add python3 openssl

COPY --chown=root:root ./root /

STOPSIGNAL SIGKILL
ENTRYPOINT [ "python", "webserver.py" ]
