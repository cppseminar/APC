# do not build this file directly, use create-docker.ps1, it wiil set up
# all the required paths and copy whatever is needed

FROM gcc:11.2-bullseye
WORKDIR /

ENV OUTPUT_PATH=/app/output
ENV SUBMISSION_PATH=/app/submission
ENV TESTS_PATH=/app/tests
ENV DATA_PATH=/app/data
ENV SUBMISSION_PROJECT=/app/submission-cmake

# install dependencies, create folders
RUN apt-get update \
    && apt-get -y install python \
    && apt-get -y install python-is-python3 \
    && apt-get -y install cmake \
    && apt-get -y install git \
    && apt-get -y install curl zip unzip tar \
    && mkdir -p /app/tester \
    && mkdir -p $TESTS_PATH \
    && mkdir -p $SUBMISSION_PATH \
    && mkdir -p $OUTPUT_PATH \
    && mkdir -p $SUBMISSION_PROJECT \
    && useradd -ms /bin/bash apc-test

# copy required files
COPY ./tester /app/tester
COPY ./tests/src $TESTS_PATH
COPY ./cpp-support $TESTS_PATH
COPY ./tests/dat $DATA_PATH
COPY ./submission-cmake $SUBMISSION_PROJECT
COPY ./tests/config.ini /app/config.ini

# install vckpg, catch2
WORKDIR /app
RUN git clone https://github.com/Microsoft/vcpkg.git \
    && ./vcpkg/bootstrap-vcpkg.sh \
    && ./vcpkg/vcpkg install catch2

# create makefiles for tests
WORKDIR $TESTS_PATH
RUN cmake -B ./build-debug -S . -DCMAKE_TOOLCHAIN_FILE=/app/vcpkg/scripts/buildsystems/vcpkg.cmake -DCMAKE_BUILD_TYPE=Debug \
    && cmake -B ./build-release -S . -DCMAKE_TOOLCHAIN_FILE=/app/vcpkg/scripts/buildsystems/vcpkg.cmake -DCMAKE_BUILD_TYPE=Release

WORKDIR /app
ENTRYPOINT ["python", "-m", "tester", "./config.ini"]
