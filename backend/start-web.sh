#!/bin/sh
# Render's dockerCommand field doesn't reliably shell-interpret `&&`
# chained inline, so the migrate-then-serve sequence lives here instead.
set -e
python manage.py migrate --noinput
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
