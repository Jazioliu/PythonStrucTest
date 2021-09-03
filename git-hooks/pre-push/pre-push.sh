#!/bin/bash
# Git hook which runs a Maven build with unit tests, but not integration tests

readonly ROOT_PATH=$(git rev-parse --show-toplevel)

check_pytest() {
    echo "Running Pytest to check for errors"

    pytest -rx -v $ROOT_PATH

    pytest_exit_code=$?
    if [ $pytest_exit_code -ne 0 ]; then
      echo "Error while testing the code"
      exit 1
    fi
}

echo "Checking projects status"
check_pytest
