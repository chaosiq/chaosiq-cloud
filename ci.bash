#!/bin/bash
set -eo pipefail

function lint () {
    echo "Checking the code syntax"
    pylama chaoscloud
}

function build () {
    echo "Building the chaosiq-cloud package"
    python setup.py build
}

function run-test () {
    echo "Running the tests"
    python3 setup.py test
}

function build-docker () {
    echo "Building the Docker image"
    docker build -t chaosiq/chaostoolkit .

    if [[ $TRAVIS_BRANCH == "master" ]]; then
      echo "Publishing to the Docker repository"
      docker push chaosiq/chaostoolkit:latest
      docker login -u ${DOCKER_USER_NAME} -p ${DOCKER_PWD}
    fi
}

function release () {
    echo "Releasing the package"
    python setup.py release

    echo "Publishing to PyPI"
    pip install twine
    twine upload dist/* -u ${PYPI_USER_NAME} -p ${PYPI_PWD}

    if [[ $TRAVIS_BRANCH == "master" ]]; then
      docker tag chaosiq/chaostoolkit:latest chaosiq/chaostoolkit:$TRAVIS_TAG
      echo "Publishing to the Docker repository"
      docker push chaosiq/chaostoolkit:$TRAVIS_TAG
    fi
}

function main () {
    lint || return 1
    build || return 1
    run-test || return 1
    build-docker || return 1

    if [[ $TRAVIS_PYTHON_VERSION =~ ^3\.5+$ ]]; then
        if [[ $TRAVIS_TAG =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "Releasing tag $TRAVIS_TAG with Python $TRAVIS_PYTHON_VERSION"
            release || return 1
        fi
    fi
}

main "$@" || exit 1
exit 0
