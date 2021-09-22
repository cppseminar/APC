FROM gcc:11.2-bullseye
WORKDIR /

ARG UNITTESTS_PATH=./example/tests
ARG CONFIG_PATH=./config.ini

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

COPY ./example/submission.cpp $SUBMISSION_PATH/submission.cpp

RUN apt-get -y install crudini \
    && crudini --set /app/config.ini paths compiler g++ \
    && crudini --set /app/config.ini paths submission $SUBMISSION_PATH \
    && crudini --set /app/config.ini paths tests /app/tests \
    && crudini --set /app/config.ini paths output $OUTPUT_PATH

WORKDIR /app
CMD python -m tester ./config.ini
