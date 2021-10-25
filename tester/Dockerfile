FROM gcc:11.2-bullseye
WORKDIR /

ARG UNITTESTS_PATH=./example/tests/hello-world
ARG CONFIG_PATH=./example/configs/hello-world/config.ini

ENV OUTPUT_PATH=/app/output
ENV SUBMISSION_PATH=/app/submission

# install python adn create folders
RUN apt-get update \
    && apt-get -y install python \
    && apt-get -y install python-is-python3 \
    && mkdir -p /app/tests \
    && mkdir -p /app/tester \
    && mkdir -p $SUBMISSION_PATH \
    && mkdir -p $OUTPUT_PATH
    
COPY ./tester /app/tester
COPY $UNITTESTS_PATH /app/tests
COPY ./cpp-support /app/tests

COPY $CONFIG_PATH /app/config.ini

RUN apt-get -y install crudini \
    && crudini --set /app/config.ini paths compiler g++ \
    && crudini --set /app/config.ini paths submission $SUBMISSION_PATH \
    && crudini --set /app/config.ini paths tests /app/tests \
    && crudini --set /app/config.ini paths output $OUTPUT_PATH

RUN useradd -ms /bin/bash apc-test
USER apc-test

WORKDIR /app
CMD python -m tester ./config.ini
