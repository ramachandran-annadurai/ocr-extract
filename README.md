# 🚀 PaddleOCR Microservice

A FastAPI-based microservice for text recognition using PaddleOCR, with support for both image and PDF processing, plus webhook integration.

## ✨ Features

- **OCR Processing**: Extract text from images using PaddleOCR
- **PDF Support**: Process PDF files with text extraction
- **Webhook Integration**: Send results to external services (like n8n)
- **RESTful API**: Clean, documented endpoints
- **CORS Support**: Cross-origin request handling
- **Health Monitoring**: Built-in health checks

## 🚀 Quick Deploy to Render

### 1. Fork/Clone this Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Deploy to Render

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `paddleocr-service`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Starter` (or your preferred plan)

### 3. Environment Variables (Optional)

The service will work with defaults, but you can set these in Render:

```bash
PYTHON_VERSION=3.11.9
WEBHOOK_ENABLED=true
DEFAULT_WEBHOOK_URL=https://your-webhook-url.com
```

### 4. Deploy!

Click **"Create Web Service"** and wait for the build to complete.

## 🧪 Testing Your Service

### 1. Health Check
```bash
curl https://your-service.onrender.com/health
```

### 2. Test OCR with Image
```bash
curl -X POST -F "file=@test-image.jpg" \
  https://your-service.onrender.com/api/v1/ocr/upload
```

### 3. Test Webhook
```bash
curl -X POST https://your-service.onrender.com/api/v1/webhook/test
```

## 📱 Using the Test Interface

1. **Open `test_endpoints.html`** in your browser
2. **Update the `BASE_URL`** in the JavaScript to your Render URL
3. **Test all endpoints** with the interactive interface

## 🔧 API Endpoints

### Core OCR
- `POST /api/v1/ocr/upload` - Upload image for OCR processing
- `POST /api/v1/ocr/base64` - Process base64 encoded image

### Webhooks
- `GET /api/v1/webhook/configs` - Get webhook configurations
- `POST /api/v1/webhook/test` - Test webhook functionality
- `GET /api/v1/webhook/debug` - Debug webhook status

### Health & Info
- `GET /health` - Service health check
- `GET /` - Service information and available endpoints
- `GET /docs` - Interactive API documentation (Swagger UI)

## 📁 Project Structure

```
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   └── services/
│       ├── ocr_service.py   # OCR processing logic
│       ├── pdf_service.py   # PDF processing logic
│       └── webhook_service.py # Webhook management
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment config
├── test_endpoints.html      # Test interface
└── README.md               # This file
```

## 🛠️ Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Service
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open Test Interface
Open `test_endpoints.html` in your browser and set `BASE_URL = 'http://localhost:8000'`

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails on Render**
   - Ensure `PYTHON_VERSION=3.11.9` is set
   - Check that all dependencies are compatible

2. **OCR Not Working**
   - Verify PaddleOCR is installed correctly
   - Check service logs for errors

3. **Webhook Issues**
   - Verify webhook URL is accessible
   - Check webhook configuration

### Logs
Check Render service logs for detailed error information.

## 📊 Performance

- **Image Processing**: ~2-5 seconds per image (depending on size)
- **PDF Processing**: ~1-3 seconds per page
- **Webhook Delivery**: Asynchronous (non-blocking)

## 🔐 Security

- CORS enabled for cross-origin requests
- File size limits enforced
- Input validation on all endpoints

## 📞 Support

If you encounter issues:
1. Check the service logs in Render
2. Verify all dependencies are compatible
3. Test endpoints individually
4. Check the `/health` endpoint for service status

## 🎯 Next Steps

After successful deployment:
1. **Test OCR functionality** with sample images
2. **Configure webhooks** for your n8n workflow
3. **Monitor performance** and adjust as needed
4. **Scale up** if required (upgrade Render plan)

---

**Happy OCR-ing! 🎉**
