# 🚂 Railway Deployment for PaddleOCR Service

This folder contains everything you need to deploy your PaddleOCR service to Railway.

## 🚀 Quick Start

```bash
# 1. Setup the deployment folder
./setup-railway.sh

# 2. Deploy to Railway
./railway-deploy.sh
```

## 📁 What's Included

| File | Purpose |
|------|---------|
| `railway.json` | Main Railway configuration |
| `nixpacks.toml` | Build configuration with Python 3.11 + ccache |
| `requirements-railway.txt` | Railway-optimized dependencies |
| `Procfile` | Alternative start command |
| `.railwayignore` | Files to exclude from deployment |
| `railway-deploy.sh` | Automated deployment script |
| `setup-railway.sh` | Setup script to copy your app files |
| `RAILWAY_DEPLOYMENT.md` | Detailed deployment guide |

## ⚡ Why Railway?

- **🚀 Faster builds** with NIXPACKS
- **🐍 Better Python support** than Render
- **💾 More memory** for PaddleOCR models
- **⚙️ Built-in ccache** for optimized builds
- **📊 Better monitoring** and metrics

## 🔧 Key Features

- ✅ **Python 3.11.9** runtime
- ✅ **ccache** automatically installed
- ✅ **Environment variables** pre-configured
- ✅ **Webhook integration** ready
- ✅ **Production optimized** settings

## 📋 Prerequisites

- [Railway Account](https://railway.app/)
- [Railway CLI](https://docs.railway.app/develop/cli)
- Node.js (for Railway CLI)

## 🎯 Next Steps

1. **Setup**: Run `./setup-railway.sh`
2. **Deploy**: Run `./railway-deploy.sh`
3. **Test**: Use your Railway URL
4. **Monitor**: Check Railway dashboard

## 📚 Documentation

- **Full Guide**: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app/)
- **NIXPACKS**: [nixpacks.com](https://nixpacks.com/)

---

**Ready to deploy?** 🚀 Run `./setup-railway.sh` to get started!
