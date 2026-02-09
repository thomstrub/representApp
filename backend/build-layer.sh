#!/bin/bash
# Build Lambda layer with dependencies

set -e

echo "Building Lambda layer..."

# Clean previous build
rm -rf layers/python layers/requirements.txt

# Create layer directory structure
mkdir -p layers/python

# Copy only runtime dependencies (exclude test dependencies)
cat > layers/requirements.txt << EOF
aws-lambda-powertools==2.30.0
pydantic>=2.0.0
boto3>=1.34.0
botocore>=1.34.0
aws-xray-sdk>=2.12.0
requests>=2.31.0
dynamodb-json>=1.3
EOF

echo "Installing dependencies for Lambda runtime (manylinux2014_x86_64)..."
# Install for Lambda runtime platform
pip3 install -r layers/requirements.txt -t layers/python \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.9 \
    --only-binary=:all: \
    --upgrade

echo "Lambda layer built successfully at layers/python"
