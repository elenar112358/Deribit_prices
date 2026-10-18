#!/usr/bin/env bash

COMPOSE="docker compose -p simplesolutions-test -f compose.test.yml"

cleanup() {
    $COMPOSE down --volumes --remove-orphans
}

trap cleanup EXIT

$COMPOSE up -d --build test_db
if [ $? -ne 0 ]; then
    exit 1
fi

$COMPOSE run --build --rm test pytest -v tests/
status=$?

exit "$status"
