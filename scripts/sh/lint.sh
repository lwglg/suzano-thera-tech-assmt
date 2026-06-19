#!/usr/bin/env bash

set -e
set -x

mypy generator
ruff check generator
ruff format generator --check
