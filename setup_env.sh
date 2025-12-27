#!/bin/bash

ENV_NAME="llm_project"

echo "Setting up conda environment: $ENV_NAME"

echo "Removing existing environment (if any)..."
conda env remove -n $ENV_NAME -y 2>/dev/null || true

echo "Creating new environment with Python 3.12..."
conda create -n $ENV_NAME python=3.12 -y

echo "Installing dependencies from requirements.txt..."
conda run -n $ENV_NAME pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  conda activate $ENV_NAME"
