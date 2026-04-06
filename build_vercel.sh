#!/bin/bash
# Build script for Vercel deployment (Root version)

echo "Building for Vercel (Root location)..."
python3 -m pip install -r requirements.txt

echo "Running collectstatic..."
cd django_project/danadjango
python3 manage.py collectstatic --noinput

echo "Build completed."
