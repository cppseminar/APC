FROM python:3.9.6-bullseye
WORKDIR /

ARG UNITTESTS_PATH=./example/tests
ARG SUBMISSION_PATH=./example/submission.cpp
ARG CONFIG_PATH=./config.ini

RUN apt-get update \
    && apt-get -y install software-properties-common \
    && add-apt-repository 'deb http://mirrors.kernel.org/ubuntu hirsute main universe' \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 871920D1991BC93C \
    && apt-get update \
    && apt-get -y install g++-11 \
    && g++-11 --version \
    && mkdir -p /app/tests \
    && mkdir -p /app/tester
    
COPY ./tester /app/tester
COPY $UNITTESTS_PATH /app/tests
COPY ./cpp-support /app/tests

COPY $CONFIG_PATH /app/config.ini

ENV OUTPUT_PATH=/app/output
ENV SUBMISSION_PATH=/app/submission

RUN apt-get -y install crudini \
    && crudini --set /app/config.ini paths compiler g++-11 \
    && crudini --set /app/config.ini paths submission $SUBMISSION_PATH \
    && crudini --set /app/config.ini paths tests /app/tests \
    && crudini --set /app/config.ini paths output $OUTPUT_PATH \
    && mkdir -p $SUBMISSION_PATH

WORKDIR /app
CMD python -m tester ./config.ini
