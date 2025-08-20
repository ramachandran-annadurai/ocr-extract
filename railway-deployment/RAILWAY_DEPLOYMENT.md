# 🚂 Railway Deployment Guide for PaddleOCR Service

This guide will help you deploy your PaddleOCR service to Railway, an alternative to Render with excellent Python support.

## 📋 Prerequisites

- [Railway Account](https://railway.app/) (Free tier available)
- [Railway CLI](https://docs.railway.app/develop/cli) installed
- Your PaddleOCR service code ready

## 🚀 Quick Deployment

### Option 1: Using the Deployment Script (Recommended)

```bash
# Navigate to railway-deployment folder
cd railway-deployment

# Make script executable
chmod +x railway-deploy.sh

# Run deployment script
./railway-deploy.sh
```

### Option 2: Manual Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project (if not already done)
railway init

# Deploy
railway up
```

## ⚙️ Configuration Files

### `railway.json`
- Main Railway configuration
- Specifies NIXPACKS builder
- Defines start command and restart policies

### `nixpacks.toml`
- NIXPACKS build configuration
- Installs Python 3.11 and ccache
- Optimized build phases

### `requirements-railway.txt`
- Railway-specific dependencies
- Includes gunicorn for production
- Optimized for Railway's environment

### `Procfile`
- Alternative start command
- Uses single worker for memory efficiency

## 🔧 Environment Variables

Railway will automatically set these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `PYTHON_VERSION` | `3.11.9` | Python runtime version |
| `WEBHOOK_ENABLED` | `true` | Enable webhook functionality |
| `DEFAULT_WEBHOOK_URL` | Your n8n URL | Webhook endpoint |
| `PADDLE_OCR_LANG` | `en` | OCR language |
| `CORS_ORIGINS` | `*` | CORS configuration |

## 📁 Project Structure

```
railway-deployment/
├── railway.json              # Railway configuration
├── nixpacks.toml            # Build configuration
├── requirements-railway.txt  # Railway dependencies
├── Procfile                 # Alternative start command
├── .railwayignore           # Ignore patterns
├── railway-deploy.sh        # Deployment script
└── RAILWAY_DEPLOYMENT.md    # This guide
```

## 🎯 Deployment Steps

### 1. **Prepare Your Code**
```bash
# Copy your app folder to railway-deployment
cp -r app/ railway-deployment/
cp requirements.txt railway-deployment/
```

### 2. **Deploy to Railway**
```bash
cd railway-deployment
railway up
```

### 3. **Set Environment Variables**
```bash
# Set webhook URL
railway variables set DEFAULT_WEBHOOK_URL=your_n8n_url

# Set other variables as needed
railway variables set DEBUG=false
```

### 4. **Check Deployment**
```bash
# View deployment status
railway status

# View logs
railway logs

# Open in browser
railway open
```

## 🔍 Monitoring & Debugging

### View Logs
```bash
# Real-time logs
railway logs --follow

# Specific service logs
railway logs --service web
```

### Check Status
```bash
# Service status
railway status

# Service details
railway service
```

### Restart Service
```bash
# Restart if needed
railway service restart
```

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `nixpacks.toml` configuration
   - Verify Python version compatibility
   - Check dependency conflicts

2. **Runtime Errors**
   - View logs: `railway logs`
   - Check environment variables
   - Verify file paths

3. **Memory Issues**
   - Reduce worker count in Procfile
   - Optimize PaddleOCR settings
   - Check memory usage in Railway dashboard

### Performance Optimization

- **Single Worker**: Use `--workers 1` for memory efficiency
- **ccache**: Automatically installed for faster builds
- **NIXPACKS**: Optimized build process
- **Environment Variables**: Configured for production

## 🌐 Accessing Your Service

After successful deployment:

1. **Get URL**: `railway status` shows your service URL
2. **Test Endpoints**: Use the URL with your API endpoints
3. **Monitor**: Check Railway dashboard for metrics
4. **Scale**: Adjust resources in Railway dashboard

## 📊 Railway vs Render

| Feature | Railway | Render |
|---------|---------|---------|
| **Python Support** | ✅ Excellent | ✅ Good |
| **Build Speed** | ⚡ Fast (NIXPACKS) | 🐌 Slower |
| **Memory** | 💾 Generous | 💾 Limited |
| **Pricing** | 💰 Competitive | 💰 Free tier |
| **Deployment** | 🚀 Simple | 🚀 Simple |

## 🎉 Success!

Your PaddleOCR service is now deployed on Railway with:
- ✅ Python 3.11.9 runtime
- ✅ ccache for optimized builds
- ✅ Automatic environment variables
- ✅ Production-ready configuration
- ✅ Webhook integration ready

## 📞 Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app/)
- **NIXPACKS**: [nixpacks.com](https://nixpacks.com/)
- **Issues**: Check Railway dashboard logs
