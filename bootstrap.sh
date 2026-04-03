#!/bin/bash
set -e
echo "Starting Flask CatBoost prediction API..."
source venv/bin/activate
exec python3 -m catBoostApp.main