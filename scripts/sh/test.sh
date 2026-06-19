#!/usr/bin/env bash

set -e
set -x

coverage run --source=generator -m pytest -ssvv
coverage report --show-missing
coverage html --title "${@-coverage}"
