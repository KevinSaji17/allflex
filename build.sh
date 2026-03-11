#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations for Django's built-in apps (admin, sessions, etc.)
python manage.py migrate --run-syncdb
