# do not build this file directly, use create-docker.ps1, it will set up
# all the required paths and copy whatever is needed

FROM gcc:13.2-bookworm
WORKDIR /

# set to 1 if results should be visible to students
ARG SHOW_RESULTS_TO_STUDENTS_ARG=0

# possible values are build and copy
# setting up compile to build will compile the submission and then copy it,
# copy will just copy the submission before build and will build it together
ARG TEST_MODE_ARG=build

ENV SHOW_RESULTS_TO_STUDENTS=$SHOW_RESULTS_TO_STUDENTS_ARG
ENV TEST_MODE=$TEST_MODE_ARG

ENV OUTPUT_PATH=/app/output
ENV SUBMISSION_PATH=/app/submission
ENV TESTS_PATH=/app/tests
ENV DATA_PATH=/app/data
ENV SUBMISSION_PROJECT=/app/submission-cmake

# install dependencies, create folders
RUN apt-get update \
    && apt-get -y install python3 \
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

# install vckpg, catch2
WORKDIR /app
RUN git clone --depth 1 --branch 2024.01.12 https://github.com/Microsoft/vcpkg.git \
    && ./vcpkg/bootstrap-vcpkg.sh \
    && ./vcpkg/vcpkg install catch2

# copy required files
COPY ./tester /app/tester
COPY ./tests/src $TESTS_PATH
COPY ./cpp-support $TESTS_PATH
COPY ./tests/dat $DATA_PATH
COPY ./submission-cmake $SUBMISSION_PROJECT
COPY ./fold2lf.py /app

# covert possible CRLF to LF in data directory
WORKDIR /app
RUN python ./fold2lf.py --folder $DATA_PATH -vv \
    && rm -f ./fold2lf.py

# create makefiles for tests
WORKDIR $TESTS_PATH
RUN cmake -B ./build-debug -S . -DCMAKE_TOOLCHAIN_FILE=/app/vcpkg/scripts/buildsystems/vcpkg.cmake -DCMAKE_BUILD_TYPE=Debug \
    && cmake -B ./build-release -S . -DCMAKE_TOOLCHAIN_FILE=/app/vcpkg/scripts/buildsystems/vcpkg.cmake -DCMAKE_BUILD_TYPE=Release

WORKDIR /app
ENTRYPOINT ["python", "-m", "tester"]
