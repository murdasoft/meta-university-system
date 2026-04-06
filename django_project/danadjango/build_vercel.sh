#!/bin/bash
# Build script for Vercel deployment

echo "Building project for Vercel..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput

echo "Build completed."
