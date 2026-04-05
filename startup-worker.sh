#!/usr/bin/env bash
set -e

exec celery -A PetShelterDjango worker --loglevel=info
