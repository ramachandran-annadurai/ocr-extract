#!/bin/bash

# Railway Deployment Script for PaddleOCR Service
# This script automates the Railway deployment process

echo "🚀 Starting Railway deployment for PaddleOCR Service..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Initialize Railway project (if not already initialized)
if [ ! -f "railway.json" ]; then
    echo "📁 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set PYTHON_VERSION=3.11.9
railway variables set WEBHOOK_ENABLED=true
railway variables set DEFAULT_WEBHOOK_URL=https://n8n.srv795087.hstgr.cloud/webhook/bf25c478-c4a9-44c5-8f43-08c3fcae51f9
railway variables set DEFAULT_WEBHOOK_METHOD=POST
railway variables set DEFAULT_WEBHOOK_TIMEOUT=30
railway variables set DEFAULT_WEBHOOK_RETRY_ATTEMPTS=3
railway variables set DEFAULT_WEBHOOK_RETRY_DELAY=1
railway variables set DEFAULT_WEBHOOK_HEADERS='{"Content-Type": "application/json"}'
railway variables set PADDLE_OCR_LANG=en
railway variables set PADDLE_OCR_USE_ANGLE_CLS=true
railway variables set PADDLE_OCR_SHOW_LOG=false
railway variables set MAX_FILE_SIZE=10485760
railway variables set CORS_ORIGINS=*

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Railway deployment completed!"
echo "🌐 Your service should be available at the Railway URL"
echo "📊 Check deployment status: railway status"
