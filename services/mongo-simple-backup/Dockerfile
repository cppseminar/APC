FROM alpine AS get_rclone

RUN apk add curl \
    && curl -O https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip rclone-current-linux-amd64.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin/ \
    && chmod 755 /usr/bin/rclone

FROM alpine AS build

RUN apk add mongodb-tools

WORKDIR /tools

COPY . .
COPY --from=get_rclone /usr/bin/rclone /usr/bin/rclone

RUN mkdir /var/dumps \
    && echo "#!/bin/sh" > ./dump.sh \
    && echo "/tools/backup.sh --url \${MONGO_CONN_STR} --output /var/dumps" >> ./dump.sh \
    && echo "rclone move /var/dumps MONGO_BACKUPS:/mongo-db-dumps --use-json-log" >> ./dump.sh \
    && chmod 0766 ./dump.sh

FROM build AS dev

RUN mv ./dump.sh /etc/periodic/15min/dump.sh
CMD crond -f -l 8

FROM build AS final

CMD ./dump.sh