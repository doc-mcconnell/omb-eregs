#!/bin/bash

set -e

docker-compose run --rm api python manage.py "$@"
