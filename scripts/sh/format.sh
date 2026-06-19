#!/bin/sh -e
set -x

ruff check generator --fix --unsafe-fixes
ruff format generator
