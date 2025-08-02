#!/bin/bash
# Build script for Render deployment

set -e

echo "Python version:"
python --version

echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
