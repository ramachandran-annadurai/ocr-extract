#!/bin/bash

# Setup script for Railway deployment
# This script copies your app files to the railway-deployment folder

echo "🚂 Setting up Railway deployment folder..."

# Create railway-deployment folder if it doesn't exist
mkdir -p railway-deployment

# Copy app folder
echo "📁 Copying app folder..."
cp -r ../app/ ./

# Copy requirements.txt
echo "📦 Copying requirements.txt..."
cp ../requirements.txt ./

# Copy webhook configs
echo "🔗 Copying webhook configurations..."
cp ../webhook_configs.json ./

# Copy .paddleocrrc if it exists
if [ -f "../.paddleocrrc" ]; then
    echo "⚙️ Copying PaddleOCR configuration..."
    cp ../.paddleocrrc ./
fi

# Copy test files
echo "🧪 Copying test files..."
cp ../test_endpoints.html ./
cp ../PaddleOCR_Service.postman_collection.json ./

# Set permissions
echo "🔐 Setting permissions..."
chmod +x railway-deploy.sh
chmod +x setup-railway.sh

echo "✅ Railway deployment folder setup complete!"
echo ""
echo "📁 Files copied:"
echo "  - app/ (your FastAPI application)"
echo "  - requirements.txt (dependencies)"
echo "  - webhook_configs.json (webhook settings)"
echo "  - test files (for testing)"
echo ""
echo "🚀 Next steps:"
echo "  1. cd railway-deployment"
echo "  2. ./railway-deploy.sh"
echo "  3. Or manually: railway up"
