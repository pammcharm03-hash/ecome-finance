#!/bin/bash
set -e

echo "=== Starting build ==="
python --version || true

echo "=== Running collectstatic ==="
python manage.py collectstatic --noinput --verbosity 2

echo "=== Running migrations ==="
python manage.py migrate --noinput --verbosity 2

echo "=== Build complete ==="